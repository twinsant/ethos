from base64 import decode
import secrets
import json
import os
import time
from urllib.parse import urlsplit

import tornado.ioloop
import tornado.web
from tornado import gen
from tornado.options import define, options, parse_command_line
from tornado.log import app_log

from slack import slack_message

from handlers.base import BaseHandler, NONCE_COOKIE, NONCE_TTL, player
from handlers.auth import SigninHandler, SignoutHandler, MeHandler
from handlers.w3 import CryptoHandler, BalanceHandler
from handlers.mud import MudWebSocket, EchoWebSocket

class MainHandler(BaseHandler):
    def get(self):
        origin = urlsplit(self.settings['ethos_origin'])
        socket_origin = f'{"wss" if origin.scheme == "https" else "ws"}://{origin.netloc}'
        self.render('index.html', csp_nonce=secrets.token_urlsafe(24), socket_origin=socket_origin,
                    walletconnect_project_id=os.environ.get('WALLETCONNECT_PROJECT_ID', ''),
                    walletconnect_chain_id=player.contract.chain_id)

class NonceHandler(BaseHandler):
    def get(self):
        now = time.time()
        nonces = self.settings['ethos_nonces']
        for nonce in list(nonces):
            if nonces[nonce] <= now:
                del nonces[nonce]
        if len(nonces) >= 10000:
            raise tornado.web.HTTPError(503, 'Too many outstanding login requests')
        n = secrets.token_hex(16)
        nonces[n] = now + NONCE_TTL
        self.set_secure_cookie(NONCE_COOKIE, n, expires_days=NONCE_TTL / 86400, **self.cookie_options())
        self.set_header('Cache-Control', 'no-store')
        self.write(n)

class SlackHandler(BaseHandler):
    def post(self):
        if not self.get_current_user():
            self.set_status(403)
            return
        try:
            data = tornado.escape.json_decode(self.request.body)
            slack_message(options.slack_secret, options.channel, data['message'])
            ret = {}
            self.write(json.dumps(ret))
        except json.decoder.JSONDecodeError:
            self.set_status(400)
            return



__DIR__ = os.path.dirname(__file__)
define("port", default=4003, help="port to listen on")
define("static", default=os.path.join(__DIR__, './static'), help="static files path")
define("template", default=os.path.join(__DIR__, './templates'), help="template files path")
define("debug", default=False, type=bool, help="debug flag")
define("secret", default=os.environ.get('ETHOS_COOKIE_SECRET', ''), help="cookie secret")

define("slack_secret", default=os.environ.get('SLACK_SECRET', ''), help="slack auth secret")
define("endpoint", default=os.environ.get('ENDPOINT', 'http://127.0.0.1:8545/'), help="Ethereum endpoint")
define("channel", default=os.environ.get('SLACK_CHANNEL', 'twinsant-com'), help="slack bot channel")
define("address", default=os.environ.get('ETHOS_ADDRESS', ''), help="address to listen on")

parse_command_line()

def make_app():
    if len(options.secret) < 32 or options.secret.startswith(('replace-', '__TODO:')):
        raise ValueError('ETHOS_COOKIE_SECRET must contain at least 32 non-placeholder characters')
    origin = os.environ.get('ETHOS_ORIGIN', 'http://127.0.0.1:4003')
    parsed = urlsplit(origin)
    if parsed.scheme not in ('http', 'https') or not parsed.netloc or parsed.path or parsed.query or parsed.fragment or parsed.username:
        raise ValueError('ETHOS_ORIGIN must be an HTTP(S) origin without a path')
    return tornado.web.Application([
        (r"/", MainHandler),

        (r"/api/nonce", NonceHandler),
        (r"/api/sign_in", SigninHandler),
        (r"/api/sign_out", SignoutHandler),
        (r"/api/me", MeHandler),

        (r"/mudapi/slack", SlackHandler),
        (r"/mudapi/crypto", CryptoHandler),
        (r"/mudapi/balance", BalanceHandler),

        (r"/ws", MudWebSocket),
        (r"/echo", EchoWebSocket),
    ], debug=options.debug, cookie_secret=options.secret, static_path=options.static,
        template_path=options.template, ethos_origin=origin, ethos_nonces={}, ethos_sessions={},
        ethos_mud_tokens={}, ethos_mud_sockets={})

if __name__ == "__main__":
    app = make_app()
    app_log.info(f'Listening {options.port} with debug mode is {options.debug}...')
    app.listen(options.port, address=options.address or None)
    tornado.ioloop.IOLoop.current().start()