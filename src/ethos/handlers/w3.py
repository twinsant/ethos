from handlers.base import BaseHandler
from w3.loot import MLoot

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
