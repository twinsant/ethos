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
    await hre.run("compile");

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
    await fs.mkdir(abiRoot, { recursive: true });

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

const networks = {
  hardhat: {
    chainId: 1337
  },
  localhost: {
    url: process.env.LOCALHOST_RPC_URL || "http://127.0.0.1:8545"
  }
};

const normalizePrivateKey = (privateKey) =>
  privateKey.startsWith("0x") ? privateKey : `0x${privateKey}`;

if (process.env.INFURA_PROJECT_ID && process.env.ROPSTEN_PRIVATE_KEY) {
  networks.ropsten = {
    url: `https://ropsten.infura.io/v3/${process.env.INFURA_PROJECT_ID}`,
    accounts: [normalizePrivateKey(process.env.ROPSTEN_PRIVATE_KEY)]
  };
}

const mumbaiPrivateKey =
  process.env.MUMBAI_PRIVATE_KEY || process.env.ROPSTEN_PRIVATE_KEY;
if (process.env.ALCHEMY_MUMBAI_API_URL && mumbaiPrivateKey) {
  networks.Mumbai = {
    url: process.env.ALCHEMY_MUMBAI_API_URL,
    accounts: [normalizePrivateKey(mumbaiPrivateKey)]
  };
}

const rinkebyPrivateKey =
  process.env.METAMASK_RINKEBY_PRIVATE_KEY || process.env.ALCHEMY_PRIVATE_KEY;
if (process.env.ALCHEMY_RINKEBY_API_URL && rinkebyPrivateKey) {
  networks.rinkeby = {
    url: process.env.ALCHEMY_RINKEBY_API_URL,
    accounts: [normalizePrivateKey(rinkebyPrivateKey)]
  };
}

module.exports = {
  solidity: "0.8.7",
  networks
};
