from geventwebsocket import WebSocketServer, WebSocketApplication, Resource
from collections import OrderedDict
from flask import Flask

class EchoApplication(WebSocketApplication):
    def on_open(self):
        print("Connection opened")

    def on_message(self, message):
        if not self.ws.closed:
            self.ws.send(message)

    def on_close(self, reason):
        print(reason)

app = EchoApplication(__name__)

if __name__ == '__main__':
    http_server = WebSocketServer(('127.0.0.1',4001), Resource(OrderedDict([('/', EchoApplication)])), debug=True)
    http_server.serve_forever()