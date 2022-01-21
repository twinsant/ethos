import json

import tornado.ioloop
import tornado.web
from tornado import websocket
from tornado import gen
from tornado.options import define, options, parse_command_line

class MainHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user_cookie = self.get_secure_cookie("user")
        if user_cookie:
            return json.loads(user_cookie)
        return None

    def get(self):
        self.render('index.html')

class MudWebSocket(websocket.WebSocketHandler):
    def check_origin(self, origin: str) -> bool:
        # TODO: fix with options
        allowed = ["http://127.0.0.1:4003"]
        if origin in allowed:
            return True
        else:
            return False

    @gen.coroutine
    def open(self):
        self.closed = False
        print("WebSocket opened")
        def on_mud_message(message):
            if not self.closed:
                self.write_message(message)
        self.mud = yield websocket.websocket_connect('ws://127.0.0.1:4001', on_message_callback=on_mud_message, subprotocols=["ascii"])

    def on_message(self, message):
        self.mud.write_message(message)

    def on_close(self):
        self.closed = True
        self.mud.close()
        print("WebSocket closed")

define("port", default=4003, help="port to listen on")
define("static", default='./static', help="static files path")
define("template", default='./templates', help="template files path")
define("debug", default=False, type=bool, help="debug flag")
define("secret", default='SET COOKIE SECRETE YOURSELF!', help="debug flag")

parse_command_line()

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/ws", MudWebSocket),
    ], debug=options.debug, cookie_secret=options.secret, static_path=options.static, template_path=options.template)

if __name__ == "__main__":
    app = make_app()
    print(f'Listening {options.port} with debug mode is {options.debug}...')
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()