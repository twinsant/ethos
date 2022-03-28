import json

from tornado import websocket
from tornado.log import app_log

from handlers.base import BaseHandler
from ethos.util import parseAcceptLanguage

from typing import (
    Any,
)

class EchoWebSocket(websocket.WebSocketHandler):
    def open(self):
        print("WebSocket opened")

    def on_message(self, message):
        self.write_message(u"You said: " + message)

    def on_close(self):
        print("WebSocket closed")

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
                            name = ens and ens or f'{input[:5]}...{input[-4:]}'
                            ipt = json.dumps({'input':input, 'name':name, 'cookie':self.cookie, 'lang':lang})
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