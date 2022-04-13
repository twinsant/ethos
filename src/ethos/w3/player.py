from datetime import datetime

from eth_typing import ContractName
from contract import EthContract

CONTRACT_ADDRESS = '0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9'

contract = EthContract(CONTRACT_ADDRESS, 'Player', endpoint='http://127.0.0.1:8545/')

if __name__ == '__main__':
    print(contract.whoami())