import json

import tornado.web

from base import BaseHandler, MYTOKEN
from slack import slack_message
from tornado.options import options

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
            ret = message
            self.set_secure_cookie(MYTOKEN, json.dumps(ret))
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
