# Development

```shell
(base) ➜  eth git:(main) ✗ pwd
/Users/ant/GitHub/ethos/eth

(base) ➜  eth git:(main) ✗ alias hh
hh='npx hardhat'

(base) ➜  eth git:(main) ✗ hh node

(base) ➜  eth git:(main) ✗ hh run scripts/MUDName.js --network localhost

(base) ➜  eth git:(main) ✗ hh deploy --network localhost --contract Player
```

# Basic Sample Hardhat Project

This project demonstrates a basic Hardhat use case. It comes with a sample contract, a test for that contract, a sample script that deploys that contract, and an example of a task implementation, which simply lists the available accounts.

Try running some of the following tasks:

```shell
npx hardhat accounts
npx hardhat compile
npx hardhat clean
npx hardhat test
npx hardhat node
node scripts/sample-script.js
npx hardhat help
```
