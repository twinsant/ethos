import tornado.ioloop
import tornado.web
from tornado import websocket
from tornado import gen

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

class MudWebSocket(websocket.WebSocketHandler):
    def check_origin(self, origin: str) -> bool:
        allowed = ["http://127.0.0.1:5000"]
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

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/ws", MudWebSocket),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(4003)
    tornado.ioloop.IOLoop.current().start()