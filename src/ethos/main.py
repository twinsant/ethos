from base64 import decode
import secrets
import json

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
import requests

from handlers.base import BaseHandler
from handlers.auth import SigninHandler, SignoutHandler, MeHandler
from handlers.w3 import LootHandler

class MainHandler(BaseHandler):
    def get(self):
        self.render('index.html')

class NonceHandler(tornado.web.RequestHandler):
    def get(self):
        n = secrets.token_urlsafe()
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

class CryptoHandler(BaseHandler):
    def post(self):
        if not self.get_current_user():
            self.set_status(403)
            return
        try:
            data = tornado.escape.json_decode(self.request.body)
            # curl -X GET "https://api.blockchain.com/v3/exchange/tickers/BTC-USD" -H  "accept: application/json"
            print(data)
            ret = requests.get('https://api.blockchain.com/v3/exchange/tickers/BTC-USD').json()
            ret = {
                'price': ret['last_trade_price']
            }
            self.write(json.dumps(ret))
        except json.decoder.JSONDecodeError:
            self.set_status(400)
            return


# https://siongui.github.io/2012/10/11/python-parse-accept-language-in-http-request-header/
def parseAcceptLanguage(acceptLanguage):
  languages = acceptLanguage.split(",")
  locale_q_pairs = []

  for language in languages:
    if language.split(";")[0] == language:
      # no q => q = 1
      locale_q_pairs.append((language.strip(), "1"))
    else:
      locale = language.split(";")[0].strip()
      q = language.split(";")[1].split("=")[1]
      locale_q_pairs.append((locale, q))

  return locale_q_pairs

class MudWebSocket(websocket.WebSocketHandler, BaseHandler):
    async def get(self, *args: Any, **kwargs: Any) -> None:
        if not self.get_current_user():
            self.set_status(403)
            return
        self.cookie = self.request.headers.get('COOKIE', '')
        self.locale = parseAcceptLanguage(self.request.headers.get('Accept-Language', 'en-US'))
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
            # print(message)
            if not self.closed and message:
                s = message.decode('utf8')
                try:
                    j = json.loads(s)
                except json.decoder.JSONDecodeError:
                    j = None
                if j:
                    if 'proxyCallback'in j:
                        cmd = j['proxyCallback']
                        if cmd == 'DID':
                            ens = self.current_user.get('ens', None)
                            if ens:
                                input = ens
                            else:
                                input = self.current_user['address']
                            # TODO: Validate lang here
                            lang = self.locale[0][0]
                            ipt = json.dumps({'input':input, 'cookie':self.cookie, 'lang':lang})
                            self.mud.write_message(ipt + '\r\n')
                        del j['proxyCallback']
                    self.write_message(message)
                else:
                    self.write_message(json.dumps({'message':s}))
        try:
            # TODO: ws using options
            mud_ws = 'ws://127.0.0.1:4001'
            self.mud = await websocket.websocket_connect(mud_ws, on_message_callback=on_mud_message, subprotocols=["ascii"])
            app_log.info(f'Mud connection {mud_ws} established.')
            self.command = ''
        except:
            self.write_message('\x1B[1;3;31mMud proxy build faild: Please contact the DM.\x1B[0m ')
            app_log.error(f'Mud connection {mud_ws} NOT established')

    async def open(self):
        self.closed = False
        await self.connect_mud()

    async def on_message(self, message):
        # print([message])
        try:
            self.command += message
            if '\r' in message:
                app_log.info(f'Sending command: {self.command}')
                self.mud.write_message(self.command)
                self.command = ''
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

        (r"/mudapi/slack", SlackHandler),
        (r"/mudapi/crypto", CryptoHandler),
        (r"/mudapi/loot", LootHandler),

        (r"/ws", MudWebSocket),
    ], debug=options.debug, cookie_secret=options.secret, static_path=options.static, template_path=options.template)

if __name__ == "__main__":
    app = make_app()
    app_log.info(f'Listening {options.port} with debug mode is {options.debug}...')
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()