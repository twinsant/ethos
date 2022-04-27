import json

import tornado.web

from handlers.base import BaseHandler, MYTOKEN
from slack import slack_message
from tornado.options import options

import w3.player as player

class SignoutHandler(tornado.web.RequestHandler):
    def post(self):
        self.clear_cookie(MYTOKEN)

class SigninHandler(BaseHandler):
    def post(self):
        data = json.loads(self.request.body)

        message = dict(data['message'])
        ens = data.get('ens')
        if ens:
            message['ens'] = ens

        if self.validate_message(message):
            slack_message(options.slack_secret, options.channel, f'{message["address"]} signed in.')
            self.set_secure_cookie(MYTOKEN, json.dumps(message))

            ret = message
            name = player.contract.names(message['address'])
            if name:
                ret['name'] = name

            self.write(json.dumps(ret))
        else:
            self.set_status(403)

class MeHandler(BaseHandler):
    def get(self):
        if self.current_user:
            data = {
                'text': 'TODO',
                'address': self.current_user['address'],
            }
            ens = self.current_user.get('ens')
            if ens:
                data['ens'] = ens
            ret = json.dumps(data)
            self.write(ret)
        else:
            self.set_status(404)
