import os
import json
import base64

from web3 import Web3

class ContractCall():
    def __init__(self, method_to_call):
        self.method_to_call = method_to_call

    def __call__(self, *args, **kwargs):
        return self.method_to_call(*args, **kwargs).call()

class EthContract:
    endpoint = 'https://mainnet.infura.io/v3/%s' % os.getenv('INFURA_PROJECT_ID', 'YOUR_INFURA_PROJECT_ID')
    web3 = Web3(Web3.HTTPProvider(endpoint))
    # web3 = Web3(Web3.IPCProvider("~/Library/Ethereum/geth.ipc"))

    def __init__(self, contract_address, abi_name):
        fn = os.path.join(os.path.dirname(__file__), f'abi/{abi_name}.json')
        with open(fn) as f:
            c = f.read()
        j = json.loads(c)
        self.abi = json.loads(j['result'])
        self.contract = self.web3.eth.contract(address=contract_address, abi=self.abi)

    def __getattr__(self, name):
        ret = None
        for i in self.abi:
            if i['type'] == 'function' and name == i['name']:
                method_to_call = getattr(self.contract.functions, name)
                ret = ContractCall(method_to_call)
        return ret

# https://etherscan.io/address/0x1dfe7Ca09e99d10835Bf73044a23B73Fc20623DF
MLOOT_CONTRACT = '0x1dfe7Ca09e99d10835Bf73044a23B73Fc20623DF'

contract = EthContract(MLOOT_CONTRACT, 'loot')

class MLoot:
    def __init__(self, address) -> None:
        self.address = address
        n = contract.balanceOf(address)
        if n > 0:
            self.idx = contract.tokenOfOwnerByIndex(address, 0)
        else:
            self.idx = -1

    def getHead(self):
        if self.idx > 0:
            return contract.getHead(self.idx)
        else:
            return None

    def getNeck(self):
        if self.idx > 0:
            return contract.getNeck(self.idx)
        else:
            return None

    def getChest(self):
        if self.idx > 0:
            return contract.getChest(self.idx)
        else:
            return None

    def getWaist(self):
        if self.idx > 0:
            return contract.getWaist(self.idx)
        else:
            return None

    def getFoot(self):
        if self.idx > 0:
            return contract.getFoot(self.idx)
        else:
            return None

    def getWeapon(self):
        if self.idx > 0:
            return contract.getWeapon(self.idx)
        else:
            return None

    def getHand(self):
        if self.idx > 0:
            return contract.getHand(self.idx)
        else:
            return None

    def getRing(self):
        if self.idx > 0:
            return contract.getRing(self.idx)
        else:
            return None

if __name__ == '__main__':
    # print(contract.totalSupply())

    address = '0x464eE0FF90B7aC76d3ec8D2a25E6926DeCC88f6d'
    # 1. balanceOf
    n = contract.balanceOf(address)
    # 2. tokenOfOwnerByIndex
    if n > 0:
        idx = contract.tokenOfOwnerByIndex(address, 0)

        print(contract.getHead(idx))
        # 3. tokenURI: base64 data
        data = contract.tokenURI(idx)
        bdata = data.split(',')[1]
        s = base64.b64decode(bdata)
        j = json.loads(s)
        img = j['image']
        idata = img.split(',')[1]
        s = base64.b64decode(idata)
        print(s)
