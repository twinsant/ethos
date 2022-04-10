import os

from web3 import Web3

class Eth:
    def __init__(self, endpoint='https://mainnet.infura.io/v3/%s' % os.getenv('INFURA_PROJECT_ID', 'YOUR_INFURA_PROJECT_ID')):
        self.web3 = Web3(Web3.HTTPProvider(endpoint))

    def balance(self, address):
        wei_balance = self.web3.eth.get_balance(Web3.toChecksumAddress(address))
        return float(Web3.fromWei(wei_balance, unit='ether'))

if __name__ == '__main__':
    address = '0x0DCd1Bf9A1b36cE34237eEaFef220932846BCD82'
    eth = Eth(endpoint='http://127.0.0.1:8545')
    print(eth.balance(address))