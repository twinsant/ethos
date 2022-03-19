from datetime import datetime
from contract import EthContract

GREETER_CONTRACT = '0x5FbDB2315678afecb367f032d93F642f64180aa3'

contract = EthContract(GREETER_CONTRACT, 'Greeter', endpoint='http://127.0.0.1:8545/')

if __name__ == '__main__':
    print(contract.greet())
    contract.setGreeting(f"Hello, Blockchain! @{datetime.now()}", view=False)
    print(contract.greet())