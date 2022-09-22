const { expect } = require("chai");
const hre = require("hardhat");
const ethers = hre.ethers;

describe("EventExample contract", function() {
  it("Deployment should save the data", async function() {
    const [owner] = await ethers.getSigners();

    const Token = await ethers.getContractFactory("EventExample");

    const hardhatToken = await Token.deploy();
    await hardhatToken.deployed();

    const CID2 = await hardhatToken.storeData(123, 456);
    expect(await hardhatToken.getCID()).to.equal(CID2);
  });
});
