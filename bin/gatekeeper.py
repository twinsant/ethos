from geventwebsocket.handler import WebSocketHandler
from geventwebsocket import WebSocketError
from gevent.pywsgi import WSGIServer
from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello'

# https://github.com/jgelens/gevent-websocket/blob/master/geventwebsocket/handler.py
@app.route('/ws')
def ws():
    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']

        closed = False
        while not closed:
            try:
                message = ws.receive()
                ws.send(message)
            except WebSocketError as e:
                print('Maybe closed', e, dir(ws))
                closed = True
    return ''

if __name__ == '__main__':
    http_server = WSGIServer(('127.0.0.1',4001), app, handler_class=WebSocketHandler)
    http_server.serve_forever()