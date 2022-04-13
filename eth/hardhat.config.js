const { task } = require("hardhat/config");

require("@nomiclabs/hardhat-waffle");

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
    const name = taskArgs.contract;

    const cf = await hre.ethers.getContractFactory(name);
    const c = await cf.deploy();
    await c.deployed();

    console.log(`${name} deployed to:`, c.address);
  });

// You need to export an object to set up your config
// Go to https://hardhat.org/config/ to learn more

/**
 * @type import('hardhat/config').HardhatUserConfig
 */
module.exports = {
  solidity: "0.8.7",
  networks: {
    hardhat: {
      chainId: 1337
    },
  }
};
