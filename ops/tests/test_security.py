import json
import secrets
import sys
import time
import types
import unittest
from datetime import datetime, timezone
from http.cookies import SimpleCookie
from pathlib import Path
from unittest.mock import patch

from eth_account import Account
from eth_account.messages import encode_defunct
from siwe.siwe import SiweMessage
import tornado.options
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application, create_signed_value

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src/ethos'))

fake_player = types.ModuleType('w3.player')
fake_player.contract = types.SimpleNamespace(
    names=lambda address: '',
    web3=types.SimpleNamespace(eth=types.SimpleNamespace(chainId=1337)),
)
with patch.dict(sys.modules, {'w3.player': fake_player}):
    from handlers import auth


class MudTestHandler(auth.BaseHandler):
    def post(self):
        if not self.get_current_user():
            raise tornado.web.HTTPError(403)
        self.write({'ok': True})


class SigninSecurityTests(AsyncHTTPTestCase):
    def get_app(self):
        auth.options = types.SimpleNamespace(slack_secret='', channel='')
        self.secret = 'test-secret-that-is-long-enough-for-tests'
        return Application(
            [(r'/api/sign_in', auth.SigninHandler), (r'/api/sign_out', auth.SignoutHandler),
             (r'/api/me', auth.MeHandler), (r'/mudapi/test', MudTestHandler)],
            cookie_secret=self.secret, ethos_origin='https://meta.example',
            ethos_nonces={}, ethos_sessions={}, ethos_mud_tokens={}, ethos_mud_sockets={},
        )

    def signed_message(self, challenge, **changes):
        account = Account.create()
        message = {
            'domain': 'meta.example', 'address': account.address, 'chainId': '1337',
            'uri': 'https://meta.example', 'version': '1', 'statement': 'EthOS',
            'type': 'Personal signature', 'nonce': challenge,
            'issuedAt': datetime.now(timezone.utc).isoformat(),
        }
        message.update(changes)
        signed = dict(message)
        signed['chain_id'] = signed.pop('chainId')
        signed['issued_at'] = signed.pop('issuedAt')
        signed.pop('type')
        raw = SiweMessage(signed).prepare_message()
        message['signature'] = Account.sign_message(encode_defunct(text=raw), account.key).signature.hex()
        return message

    def nonce_cookie(self, nonce):
        self._app.settings['ethos_nonces'][nonce] = time.time() + 300
        value = create_signed_value(self.secret, 'ethos_nonce', nonce).decode()
        return f'ethos_nonce={value}'

    def signin(self, message, cookie, origin='https://meta.example', ens=None):
        return self.fetch('/api/sign_in', method='POST',
                          headers={'Origin': origin, 'Cookie': cookie, 'Content-Type': 'application/json'},
                          body=json.dumps({'message': message, 'ens': ens}))

    def test_one_time_nonce_and_revocable_session(self):
        nonce = secrets.token_hex(16)
        cookie = self.nonce_cookie(nonce)
        message = self.signed_message(nonce)
        response = self.signin(message, cookie, ens='someone-else.eth')
        self.assertEqual(response.code, 200)
        self.assertNotIn('ens', json.loads(response.body))
        self.assertEqual(self.signin(message, cookie).code, 403)
        cookies = SimpleCookie()
        for value in response.headers.get_list('Set-Cookie'):
            cookies.load(value)
        self.assertTrue(cookies['mytoken']['httponly'])
        self.assertTrue(cookies['mytoken']['secure'])
        session_cookie = f'mytoken={cookies["mytoken"].value}'
        self.assertEqual(self.fetch('/api/me', headers={'Cookie': session_cookie}).code, 200)
        self._app.settings['ethos_mud_tokens']['mud-token'] = next(iter(self._app.settings['ethos_sessions']))
        mud_socket = unittest.mock.Mock()
        self._app.settings['ethos_mud_sockets']['mud-token'] = mud_socket
        mud_headers = {'Cookie': 'ethos_mud=mud-token', 'Content-Type': 'application/json'}
        self.assertEqual(self.fetch('/mudapi/test', method='POST', headers=mud_headers, body='{}').code, 200)
        self.assertEqual(self.fetch('/api/me', headers={'Cookie': 'ethos_mud=mud-token'}).code, 204)
        self.assertEqual(self.fetch('/mudapi/test', method='POST', body='{}',
                                    headers={**mud_headers, 'Origin': 'https://attacker.example'}).code, 403)
        self.assertEqual(self.fetch('/mudapi/test', method='POST', body='{}',
                                    headers={**mud_headers, 'Content-Type': 'text/plain'}).code, 415)
        self.assertEqual(self.fetch('/api/sign_out', method='POST', body='',
                                    headers={'Origin': 'https://meta.example', 'Cookie': session_cookie}).code, 200)
        self.assertEqual(self.fetch('/api/me', headers={'Cookie': session_cookie}).code, 204)
        self.assertEqual(self.fetch('/mudapi/test', method='POST', headers=mud_headers, body='{}').code, 403)
        mud_socket.close.assert_called_once()

    def test_rejects_wrong_domain_chain_nonce_and_origin(self):
        for changes, origin in [
            ({'domain': 'attacker.example', 'uri': 'https://attacker.example'}, 'https://meta.example'),
            ({'chainId': '1'}, 'https://meta.example'),
            ({'nonce': 'wrongnonce'}, 'https://meta.example'),
            ({}, 'https://attacker.example'),
            ({'issuedAt': '2020-01-01T00:00:00Z'}, 'https://meta.example'),
        ]:
            nonce = secrets.token_hex(16)
            response = self.signin(self.signed_message(nonce, **changes), self.nonce_cookie(nonce), origin)
            self.assertEqual(response.code, 403, changes)


class LootZeroTests(unittest.TestCase):
    def test_token_zero_is_not_treated_as_missing(self):
        fake_contract = types.SimpleNamespace(balanceOf=lambda address: 1,
                                              tokenOfOwnerByIndex=lambda address, index: 0,
                                              getHead=lambda index: f'head-{index}')
        fake_module = types.ModuleType('w3.contract')
        fake_module.EthContract = lambda *args, **kwargs: fake_contract
        with patch.dict(sys.modules, {'w3.contract': fake_module}):
            import importlib.util
            spec = importlib.util.spec_from_file_location('loot_security_test', ROOT / 'src/ethos/w3/loot.py')
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        self.assertEqual(module.MLoot('address').getHead(), 'head-0')
