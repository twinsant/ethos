import json

import tornado.web
from siwe import siwe
import w3.player as player

MYTOKEN = 'mytoken'

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user_cookie = self.get_secure_cookie(MYTOKEN)
        if user_cookie:
            message = json.loads(user_cookie)
            if self.validate_message(message):
                name = player.contract.names(message['address'])
                if name:
                    message['name'] = name
                return message
            else:
                return None
        return None

    def validate_message(self, message):
        '''
        {'domain': '127.0.0.1:4003',
         'address': '0x464eE0FF90B7aC76d3ec8D2a25E6926DeCC88f6d',
         'chainId': '1',
         'uri': 'http://127.0.0.1:4003',
         'version': '1',
         'statement': 'EthOS',
         'type': 'Personal signature',
         'nonce': '...',
         'issuedAt': '2022-01-24T02:32:10.239Z',
         'signature': '...'
         }
        '''
        ret = False
        
        if 'chainId' in message:
            message['chain_id'] = message['chainId']
            del message['chainId']
        if 'issuedAt' in message:
            message['issued_at'] = message['issuedAt']
            del message['issuedAt']
        FIELDS_CHECK = ['ens', 'domain', 'address', 'chainId', 'chain_id', 'uri', 'version', 'statement', 'type', 'nonce', 'issuedAt', 'issued_at', 'signature']
        for k, v in message.items():
            if k not in FIELDS_CHECK:
                app_log.warn(f'Message filed invalid: {k}!')
                return False
        siwe_message = siwe.SiweMessage(message)
        _signature = message['signature']
        try:
            siwe_message.validate(_signature)
            ret = True
        except siwe.ValidationError:
            app_log.warn(f'Address { message["address"] } sign in failed.')

        return ret
