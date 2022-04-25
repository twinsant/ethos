const { expect } = require("chai");
const { ethers } = require("hardhat");

// https://docs.openzeppelin.com/learn/writing-automated-tests?pref=hardhat

// Import utilities from Test Helpers
const { expectRevert } = require('@openzeppelin/test-helpers');

// Load compiled artifacts
const Player = artifacts.require('Player');

// Start test block
contract('Player', function ([ owner, other ]) {
  beforeEach(async function () {
    this.player = await Player.new({ from: owner });
    this.alice = 'alice';
  });

  it('claim without ethers', async function () {
    // Test a transaction reverts
    await expectRevert(
      this.player.claim(this.alice, { from: other }),
      '0.01 Ethers needed.',
    );
  });
});