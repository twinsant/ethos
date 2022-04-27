import os
from web3 import Web3

from eth_typing import ContractName
from w3.contract import EthContract

contract = EthContract('Player', endpoint=os.environ.get('ENDPOINT', 'http://127.0.0.1:8545/'))

if __name__ == '__main__':
    print(contract.names(Web3.toChecksumAddress('0x70997970C51812dc3A010C7d01b50e0d17dc79C8')))