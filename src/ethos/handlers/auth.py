import json
import secrets
import time

import tornado.web
from tornado.options import options

from handlers.base import BaseHandler, MYTOKEN, NONCE_COOKIE, SESSION_TTL
from slack import slack_message


class SignoutHandler(BaseHandler):
    def post(self):
        self.require_origin()
        token = self.get_secure_cookie(MYTOKEN)
        if token:
            session_id = token.decode('utf-8')
            self.settings['ethos_sessions'].pop(session_id, None)
            for mud_token, owner in list(self.settings['ethos_mud_tokens'].items()):
                if owner == session_id:
                    self.settings['ethos_mud_tokens'].pop(mud_token, None)
                    socket = self.settings['ethos_mud_sockets'].pop(mud_token, None)
                    if socket:
                        socket.close()
        self.clear_cookie(MYTOKEN)


class SigninHandler(BaseHandler):
    def post(self):
        self.require_origin()
        if self.request.headers.get('Content-Type', '').split(';')[0] != 'application/json':
            raise tornado.web.HTTPError(415)
        try:
            data = json.loads(self.request.body)
            message = data['message']
        except (ValueError, KeyError, TypeError):
            raise tornado.web.HTTPError(400)
        cookie = self.get_secure_cookie(NONCE_COOKIE, max_age_days=1)
        self.clear_cookie(NONCE_COOKIE)
        if not cookie:
            raise tornado.web.HTTPError(403)
        nonce = cookie.decode('utf-8')
        expires = self.settings['ethos_nonces'].pop(nonce, 0)
        if expires <= time.time():
            raise tornado.web.HTTPError(403)
        user = self.validate_message(message, nonce)
        if not user:
            raise tornado.web.HTTPError(403)
        slack_message(options.slack_secret, options.channel, f'{user["address"]} signed in.')
        now = time.time()
        sessions = self.settings['ethos_sessions']
        for token in list(sessions):
            if sessions[token]['expires'] <= now:
                del sessions[token]
        token = secrets.token_urlsafe(32)
        sessions[token] = {'user': user, 'expires': now + SESSION_TTL}
        self.set_secure_cookie(MYTOKEN, token, expires_days=SESSION_TTL / 86400, **self.cookie_options())
        self.write({'address': user['address'], 'chainId': user['chain_id']})


class MeHandler(BaseHandler):
    def get(self):
        if self.current_user:
            self.write({
                'text': 'TODO',
                'address': self.current_user['address'],
                'chainId': self.current_user['chain_id'],
            })
        else:
            self.set_status(204)
