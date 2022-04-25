const { ethers } = require("hardhat");

// https://docs.openzeppelin.com/learn/writing-automated-tests?pref=hardhat

// Import utilities from Test Helpers
const { expectRevert } = require('@openzeppelin/test-helpers');
const { assert } = require("chai");

// Load compiled artifacts
const Player = artifacts.require('Player');

// Start test block
contract('Player', function ([ owner, other ]) {
  beforeEach(async function () {
    this.player = await Player.new({ from: owner });
    this.alice = 'alice';
    this.bob = 'bob';
    this.fee = ethers.utils.parseEther('0.01').toHexString();
    this.otherWithoutFee = { from: other };
    this.otherWithFee = { from: other, value: this.fee };
    this.ownerWithFee = { from: owner, value: this.fee };
  });

  it('claim without ethers', async function () {
    await expectRevert(
      this.player.claim(this.alice, this.otherWithoutFee),
      '0.01 Ethers needed.',
    );
  });

  it('claim with not enough ethers', async function () {
    let wei = ethers.utils.parseEther('0.009').toHexString();
    await expectRevert(
      this.player.claim(this.alice, { from: other, value: wei}),
      '0.01 Ethers needed.',
    );
  });

  it('claim with empty name', async function () {
    await expectRevert(
      this.player.claim("", this.otherWithFee),
      'Empty string not allowed.',
    );
  });

  it('claim', async function () {
    await this.player.claim(this.alice, this.otherWithFee);
    let whoami = await this.player.whoami(this.otherWithoutFee);
    let whois = await this.player.whois(this.alice, this.otherWithoutFee);
    assert.equal(whoami, this.alice);
    assert.equal(whois, other);
  });

  it('claim again', async function () {
    await this.player.claim(this.alice, this.otherWithFee);
    await this.player.claim(this.bob, this.otherWithFee);

    let whoami = await this.player.whoami(this.otherWithoutFee);
    let whois_bob = await this.player.whois(this.bob, this.otherWithoutFee);
    let whois_alice = await this.player.whois(this.alice, this.otherWithoutFee);

    assert.equal(whoami, this.bob);
    assert.equal(whois_bob, other);
    assert.equal(whois_alice, ethers.constants.AddressZero);
  });

  it('claim same', async function () {
    await this.player.claim(this.alice, this.otherWithFee);
    await this.player.claim(this.alice, this.otherWithFee);
    let whoami = await this.player.whoami(this.otherWithoutFee);
    let whois = await this.player.whois(this.alice, this.otherWithoutFee);
    assert.equal(whoami, this.alice);
    assert.equal(whois, other);
  });

  it('claim taken', async function () {
    await this.player.claim(this.alice, this.otherWithFee);
    await expectRevert(
      this.player.claim(this.alice, this.ownerWithFee),
      'Name taken.',
    );
  });
});