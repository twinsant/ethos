import json
import time
from datetime import datetime, timezone
from urllib.parse import urlsplit

import tornado.web
from siwe import siwe

import w3.player as player

MYTOKEN = 'mytoken'
NONCE_COOKIE = 'ethos_nonce'
NONCE_TTL = 300
SESSION_TTL = 12 * 60 * 60


class BaseHandler(tornado.web.RequestHandler):
    def prepare(self):
        origin = self.request.headers.get('Origin')
        if self.request.method not in ('GET', 'HEAD', 'OPTIONS') and origin and origin != self.settings['ethos_origin']:
            raise tornado.web.HTTPError(403, 'Invalid request origin')
        if self.request.path.startswith('/mudapi/') and self.request.method == 'POST':
            if self.request.headers.get('Content-Type', '').split(';')[0] != 'application/json':
                raise tornado.web.HTTPError(415)

    def cookie_options(self):
        return {
            'httponly': True,
            'secure': urlsplit(self.settings['ethos_origin']).scheme == 'https',
            'samesite': 'Strict',
        }

    def require_origin(self):
        if self.request.headers.get('Origin') != self.settings['ethos_origin']:
            raise tornado.web.HTTPError(403, 'Invalid request origin')

    def get_current_user(self):
        token = self.get_secure_cookie(MYTOKEN, max_age_days=SESSION_TTL / 86400)
        if token:
            token = token.decode('utf-8')
        elif (
            self.request.path.startswith('/mudapi/')
            and self.request.remote_ip in ('127.0.0.1', '::1')
            and not self.request.headers.get('Origin')
        ):
            token = self.settings['ethos_mud_tokens'].get(self.get_cookie('ethos_mud', ''))
        if not token:
            return None
        session = self.settings['ethos_sessions'].get(token)
        if not session:
            return None
        if session['expires'] <= time.time():
            del self.settings['ethos_sessions'][token]
            return None
        user = dict(session['user'])
        name = player.contract.names(user['address'])
        if name:
            user['name'] = name
            user['nameClaimed'] = 1
        else:
            user['nameClaimed'] = 0
        return user

    def validate_message(self, message, nonce):
        if not isinstance(message, dict):
            return None
        fields = {
            'domain', 'address', 'chainId', 'uri', 'version', 'statement',
            'type', 'nonce', 'issuedAt', 'signature',
        }
        if set(message) - fields:
            return None
        try:
            origin = self.settings['ethos_origin']
            if (
                message['domain'] != urlsplit(origin).netloc
                or message['uri'] != origin
                or message['version'] != '1'
                or message['nonce'] != nonce
                or int(message['chainId']) != player.contract.web3.eth.chainId
            ):
                return None
            issued_at = datetime.fromisoformat(message['issuedAt'].replace('Z', '+00:00'))
            if issued_at.tzinfo is None:
                return None
            age = (datetime.now(timezone.utc) - issued_at).total_seconds()
            if age < -30 or age > NONCE_TTL:
                return None
            signed = dict(message)
            signed['chain_id'] = signed.pop('chainId')
            signed['issued_at'] = signed.pop('issuedAt')
            signature = signed.pop('signature')
            signed.pop('type', None)
            siwe.SiweMessage(signed).validate(signature)
            return {'address': signed['address'], 'chain_id': str(signed['chain_id'])}
        except (KeyError, TypeError, ValueError, siwe.ValidationError):
            return None
