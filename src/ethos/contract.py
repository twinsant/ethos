import os
import json

from web3 import Web3

class ContractCall():
    def __init__(self, w3, method_to_call):
        self.w3 = w3
        self.method_to_call = method_to_call

    def __call__(self, *args, **kwargs):
        if 'view' in kwargs and kwargs['view'] == False:
            del kwargs['view']
            tx_hash = self.method_to_call(*args, **kwargs).transact()
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return tx_receipt
        else:
            return self.method_to_call(*args, **kwargs).call()

class EthContract:
    def __init__(self, contract_address, abi_name, endpoint='https://mainnet.infura.io/v3/%s' % os.getenv('INFURA_PROJECT_ID', 'YOUR_INFURA_PROJECT_ID')):
        self.web3 = Web3(Web3.HTTPProvider(endpoint))
        # web3 = Web3(Web3.IPCProvider("~/Library/Ethereum/geth.ipc"))

        fn = os.path.join(os.path.dirname(__file__), f'abi/{abi_name}.json')
        with open(fn) as f:
            c = f.read()
        self.abi = json.loads(c)
        self.contract = self.web3.eth.contract(address=contract_address, abi=self.abi)

    def __getattr__(self, name):
        ret = None
        for i in self.abi:
            if i['type'] == 'function' and name == i['name']:
                method_to_call = getattr(self.contract.functions, name)
                ret = ContractCall(self.web3, method_to_call)
        return ret
