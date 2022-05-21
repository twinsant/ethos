const { task } = require("hardhat/config");

const path = require('path');
const { promises: fs } = require("fs");
require("@nomiclabs/hardhat-waffle");
require("@nomiclabs/hardhat-truffle5");

// This is a sample Hardhat task. To learn how to create your own go to
// https://hardhat.org/guides/create-task.html
task("accounts", "Prints the list of accounts", async (taskArgs, hre) => {
  const accounts = await hre.ethers.getSigners();

  for (const account of accounts) {
    console.log(account.address);
  }
});

task("balance", "Prints an account's balance")
  .addParam("account", "The account's address")
  .setAction(async (taskArgs, hre) => {
    const balance = await hre.ethers.provider.getBalance(taskArgs.account);
    console.log(`${taskArgs.account} : ${hre.ethers.utils.formatEther(balance)} ETH`)
});

task("deploy", "Deploy contract")
  .addParam("contract", "The contract name")
  .setAction(async (taskArgs, hre) => {
    // Deploy contract
    const name = taskArgs.contract;

    const cf = await hre.ethers.getContractFactory(name);
    const c = await cf.deploy();
    await c.deployed();

    console.log(`${name} deployed to:`, c.address);

    // Make abi dir
    const chainId = await (await hre.ethers.provider.getNetwork()).chainId;
    const root = hre.config.paths.root;
    const abiRoot = path.join(root, `../src/ethos/static/abi/${chainId}`)
    try {
      await fs.stat(abiRoot);
    } catch (e) {
      await fs.mkdir(abiRoot);
    }

    // Read abi data
    const buildFile = path.join(hre.config.paths.artifacts, `./contracts/${name}.sol/${name}.json`);
    let t = await fs.readFile(buildFile);
    let j = JSON.parse(t);

    // Write abi file
    const data = {
      'address': c.address,
      'abi': j['abi']
    }
    let abiFile = path.join(abiRoot, `${name}.json`)
    await fs.writeFile(abiFile, JSON.stringify(data))
  });

// You need to export an object to set up your config
// Go to https://hardhat.org/config/ to learn more

/**
 * @type import('hardhat/config').HardhatUserConfig
 * read from env by process
 * const CONTRACT_ADDRESS = process.env.REACT_APP_CONTRACT_ADDRESS;
 */
const INFURA_PROJECT_ID = process.env.INFURA_PROJECT_ID;
module.exports = {
  solidity: "0.8.7",
  networks: {
    hardhat: {
      chainId: 1337
    },
    ropsten: {
      url: `https://ropsten.infura.io/v3/${INFURA_PROJECT_ID}`,
      accounts: [`0x${ROPSTEN_PRIVATE_KEY}`]
    },
    Mumbai: {
      url: `https://ropsten.infura.io/v3/${INFURA_PROJECT_ID}`,
      accounts: [`0x${ROPSTEN_PRIVATE_KEY}`]
    }
  }
};
