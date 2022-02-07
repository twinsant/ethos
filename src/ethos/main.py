import secrets
import json

from siwe import siwe

import tornado.ioloop
import tornado.web
from tornado import websocket
from tornado import gen
from tornado.options import define, options, parse_command_line
from tornado.log import app_log

from typing import (
    Any,
)

from slack import slack_message

MYTOKEN = 'mytoken'

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user_cookie = self.get_secure_cookie(MYTOKEN)
        if user_cookie:
            message = json.loads(user_cookie)
            if self.validate_message(message):
                return message
            else:
                return None
        return None

    def validate_message(self, message):
        '''
        {'domain': '127.0.0.1:4003',
         'address': '0x464eE0FF90B7aC76d3ec8D2a25E6926DeCC88f6d',
         'chainId': '1',
         'uri': 'http://127.0.0.1:4003',
         'version': '1',
         'statement': 'EthOS',
         'type': 'Personal signature',
         'nonce': '...',
         'issuedAt': '2022-01-24T02:32:10.239Z',
         'signature': '...'
         }
        '''
        ret = False

        if 'chainId' in message:
            message['chain_id'] = message['chainId']
            del message['chainId']
        if 'issuedAt' in message:
            message['issued_at'] = message['issuedAt']
            del message['issuedAt']
        FIELDS_CHECK = ['ens', 'domain', 'address', 'chainId', 'chain_id', 'uri', 'version', 'statement', 'type', 'nonce', 'issuedAt', 'issued_at', 'signature']
        for k, v in message.items():
            if k not in FIELDS_CHECK:
                app_log.warn(f'Message filed invalid: {k}!')
                return False
        siwe_message = siwe.SiweMessage(message)
        try:
            siwe_message.validate()
            ret = True
        except siwe.ValidationError:
            app_log.warn(f'Address { message["address"] } sign in failed.')

        return ret

class MainHandler(BaseHandler):
    def get(self):
        self.render('index.html')

class MeHandler(BaseHandler):
    def get(self):
        if self.current_user:
            data = {
                'text': 'TODO',
                'address': self.current_user['address'],
                'ens': self.current_user['ens'],
            }
            ret = json.dumps(data)
            self.write(ret)
        else:
            self.set_status(404)

class NonceHandler(tornado.web.RequestHandler):
    def get(self):
        n = secrets.token_urlsafe()
        self.write(n)

class SignoutHandler(tornado.web.RequestHandler):
    def post(self):
        self.clear_cookie(MYTOKEN)

class SigninHandler(BaseHandler):
    def post(self):
        data = json.loads(self.request.body)

        message = dict(data['message'])
        message['ens'] = data['ens']

        if self.validate_message(message):
            slack_message(options.slack_secret, options.channel, f'{message["address"]} signed in.')
            ret = message
            self.set_secure_cookie(MYTOKEN, json.dumps(ret))
            self.write(json.dumps(ret))
        else:
            self.set_status(403)

class MudWebSocket(websocket.WebSocketHandler, BaseHandler):
    async def get(self, *args: Any, **kwargs: Any) -> None:
        if not self.get_current_user():
            self.set_status(403)
            return
        await super(MudWebSocket, self).get(*args, **kwargs)

    def check_origin(self, origin: str) -> bool:
        app_log.info(f'Checking origin: {origin} ...')
        # TODO: fix with options
        allowed = ["http://127.0.0.1:4003"]
        if origin in allowed:
            return True
        else:
            return False

    async def connect_mud(self):
        def on_mud_message(message):
            if not self.closed and message:
                s = message.decode('utf8')
                try:
                    j = json.loads(s)
                except json.decoder.JSONDecodeError:
                    j = None
                if j:
                    self.write_message(message)
                else:
                    self.write_message(json.dumps({'message':s}))
        try:
            # TODO: ws using options
            mud_ws = 'ws://127.0.0.1:4001'
            self.mud = await websocket.websocket_connect(mud_ws, on_message_callback=on_mud_message, subprotocols=["ascii"])
            app_log.info(f'Mud connection {mud_ws} established.')
        except:
            self.write_message('\x1B[1;3;31mMud proxy build faild: Please contact the DM.\x1B[0m ')
            app_log.error(f'Mud connection {mud_ws} NOT established')

    async def open(self):
        self.closed = False
        await self.connect_mud()

    async def on_message(self, message):
        try:
            app_log.info(f'Sending command: {message}')
            self.mud.write_message(message)
        except websocket.WebSocketClosedError:
            app_log.error(f'Mud connection lost!')
            self.closed = True

    def on_close(self):
        self.closed = True
        if self.mud:
            self.mud.close()

define("port", default=4003, help="port to listen on")
define("static", default='./static', help="static files path")
define("template", default='./templates', help="template files path")
define("debug", default=False, type=bool, help="debug flag")
define("secret", default='__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__', help="cookie secret")

define("slack_secret", default='__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__', help="slack auth secret")
define("channel", default='twinsant-com', help="slack bot channel")

parse_command_line()

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),

        (r"/api/nonce", NonceHandler),
        (r"/api/sign_in", SigninHandler),
        (r"/api/sign_out", SignoutHandler),
        (r"/api/me", MeHandler),

        (r"/ws", MudWebSocket),
    ], debug=options.debug, cookie_secret=options.secret, static_path=options.static, template_path=options.template)

if __name__ == "__main__":
    app = make_app()
    app_log.info(f'Listening {options.port} with debug mode is {options.debug}...')
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()