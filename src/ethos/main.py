from base64 import decode
import secrets
import json

import tornado.ioloop
import tornado.web
from tornado import gen
from tornado.options import define, options, parse_command_line
from tornado.log import app_log

from slack import slack_message

from handlers.base import BaseHandler
from handlers.auth import SigninHandler, SignoutHandler, MeHandler
from handlers.w3 import LootHandler, CryptoHandler
from handlers.mud import MudWebSocket

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