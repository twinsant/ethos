from datetime import datetime
from contract import EthContract

GREETER_CONTRACT = '0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0'

contract = EthContract(GREETER_CONTRACT, 'Greeter', endpoint='http://127.0.0.1:8545/')

if __name__ == '__main__':
    print(contract.greet())
    contract.setGreeting(f"Hello, Blockchain! @{datetime.now()}", update=True)
    print(contract.greet())