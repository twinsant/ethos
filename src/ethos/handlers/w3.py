import json

import requests
import tornado.web
from tornado.options import options

from handlers.base import BaseHandler
from w3.loot import MLoot
from w3.eth import Eth

class LootHandler(BaseHandler):
    def post(self):
        user = self.get_current_user()
        if not user:
            self.set_status(403)
            return
        try:
            mloot = MLoot(user['address'])
            ret = {
                'head': mloot.getHead(),
                'neck': mloot.getNeck(),
                'chest': mloot.getChest(),
                'waist': mloot.getWaist(),
                'foot': mloot.getFoot(),
                'hand': mloot.getHand(),
                'weapon': mloot.getWeapon(),
                'ring': mloot.getRing(),
            }
            self.write(json.dumps(ret))
        except json.decoder.JSONDecodeError:
            self.set_status(400)
            return

class CryptoHandler(BaseHandler):
    def post(self):
        if not self.get_current_user():
            self.set_status(403)
            return
        try:
            data = tornado.escape.json_decode(self.request.body)
            # curl -X GET "https://api.blockchain.com/v3/exchange/tickers/BTC-USD" -H  "accept: application/json"
            print(data)
            ret = requests.get('https://api.blockchain.com/v3/exchange/tickers/BTC-USD').json()
            ret = {
                'price': ret['last_trade_price']
            }
            self.write(json.dumps(ret))
        except json.decoder.JSONDecodeError:
            self.set_status(400)
            return

class BalanceHandler(BaseHandler):
    def post(self):
        user = self.get_current_user()
        if not user:
            self.set_status(403)
            return
        try:
            eth = Eth(endpoint=options.endpoint)
            try:
                balance = eth.balance(user['address'])
                ret = {
                    'balance': balance,
                }
            except requests.exceptions.ConnectionError:
                ret = {
                    'error': True,
                }
            self.write(json.dumps(ret))
        except json.decoder.JSONDecodeError:
            self.set_status(400)
            return