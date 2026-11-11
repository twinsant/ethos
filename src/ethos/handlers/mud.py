import json
import secrets
import time
from urllib.parse import urlsplit

from tornado import httpclient, websocket
from tornado.log import app_log

from handlers.base import BaseHandler, MYTOKEN
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
        self.locale = parseAcceptLanguage(self.request.headers.get('Accept-Language', 'en-US'))
        await super(MudWebSocket, self).get(*args, **kwargs)

    def check_origin(self, origin: str) -> bool:
        try:
            parsed_origin = urlsplit(origin)
        except ValueError:
            app_log.warning("Rejecting malformed WebSocket origin")
            return False
        return (
            parsed_origin.scheme in ('http', 'https')
            and not parsed_origin.path
            and not parsed_origin.query
            and not parsed_origin.fragment
            and origin == self.settings['ethos_origin']
        )

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
                            # TODO: Refactoring duplicated code on base.py, auth.py
                            chain_id = self.current_user['chain_id']
                            mud_name = self.current_user.get('name', None)
                            input = self.current_user['address']
                            # TODO: Validate lang here
                            lang = self.locale[0][0]

                            if mud_name and len(mud_name) <= 32 and all(
                                c in 'abcdefghijklmnopqrstuvwxyz0123456789_' for c in mud_name
                            ):
                                name = mud_name
                                nameClaimed = 1
                            else:
                                name = f'{input[:5]}...{input[-4:]}'
                                nameClaimed = 0

                            ipt = json.dumps({'chain_id':chain_id, 'input':input, 'name':name, 'nameClaimed':nameClaimed, 'cookie':self.cookie, 'lang':lang})
                            self.mud.write_message(ipt + '\r\n')
                            self.did_ready = True
                        del j['proxyCallback']
                    self.write_message(json.dumps(j))
                else:
                    self.write_message(json.dumps({'message':s}))
        try:
            # TODO: ws using options
            mud_ws = 'ws://127.0.0.1:4001'
            self.mud = await websocket.websocket_connect(mud_ws, on_message_callback=on_mud_message, subprotocols=["ascii"])
            app_log.info(f'Mud connection {mud_ws} established.')
            self.command = ''
        except (OSError, httpclient.HTTPClientError):
            self.write_message(json.dumps({'message':'\x1B[1;3;31mMud proxy build faild: Please contact the DM.\x1B[0m \n'}))
            app_log.exception('Mud connection %s not established', mud_ws)
            self.close()

    async def open(self):
        self.closed = False
        self.did_ready = False
        self.mud = None
        self.mud_token = secrets.token_urlsafe(32)
        token = self.get_secure_cookie(MYTOKEN)
        if not token:
            self.close()
            return
        self.settings['ethos_mud_tokens'][self.mud_token] = token.decode('utf-8')
        self.settings['ethos_mud_sockets'][self.mud_token] = self
        self.cookie = f'ethos_mud={self.mud_token}'
        await self.connect_mud()

    async def on_message(self, message):
        if not self.did_ready or not isinstance(message, str):
            app_log.warning('Rejecting MUD input before identity handshake')
            self.close()
            return
        token = self.settings['ethos_mud_tokens'].get(self.mud_token)
        session = self.settings['ethos_sessions'].get(token)
        if not session or session['expires'] <= time.time():
            self.close()
            return
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
        if getattr(self, 'mud_token', None):
            self.settings['ethos_mud_tokens'].pop(self.mud_token, None)
            self.settings['ethos_mud_sockets'].pop(self.mud_token, None)
        if getattr(self, 'mud', None):
            self.mud.close()