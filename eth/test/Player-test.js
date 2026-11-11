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
      'Exact 0.01 ETH required.',
    );
  });

  it('claim with not enough ethers', async function () {
    let wei = ethers.utils.parseEther('0.009').toHexString();
    await expectRevert(
      this.player.claim(this.alice, { from: other, value: wei}),
      'Exact 0.01 ETH required.',
    );
  });

  it('claim with empty name', async function () {
    await expectRevert(
      this.player.claim("", this.otherWithFee),
      'Invalid name length.',
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
    await expectRevert(
      this.player.claim(this.alice, this.otherWithFee),
      'Name already claimed.',
    );
    let whoami = await this.player.whoami(this.otherWithoutFee);
    let whois = await this.player.whois(this.alice, this.otherWithoutFee);
    assert.equal(whoami, this.alice);
    assert.equal(whois, other);
  });

  it('rejects overpayment', async function () {
    await expectRevert(
      this.player.claim(this.alice, { from: other, value: ethers.utils.parseEther('0.02').toHexString() }),
      'Exact 0.01 ETH required.',
    );
  });

  it('prevents renouncing ownership of the fee-collecting contract', async function () {
    await expectRevert(this.player.renounceOwnership({ from: owner }), 'Ownership cannot be renounced.');
  });

  it('requires the new owner to accept ownership', async function () {
    await this.player.transferOwnership(other, { from: owner });
    assert.equal(await this.player.owner(), owner);
    await expectRevert(this.player.acceptOwnership({ from: owner }), 'Not pending owner.');
    await this.player.acceptOwnership({ from: other });
    assert.equal(await this.player.owner(), other);
    assert.equal(await this.player.pendingOwner(), ethers.constants.AddressZero);
  });

  it('accepts only lowercase ASCII names of at most 32 characters', async function () {
    for (const name of ['Alice', 'alice bob', 'alice\x1b', 'alice.eth', 'a'.repeat(33)]) {
      await expectRevert.unspecified(this.player.claim(name, this.otherWithFee));
    }
    const name = 'a_0' + 'b'.repeat(29);
    await this.player.claim(name, this.otherWithFee);
    assert.equal(await this.player.whois(name), other);
  });

  it('claim taken', async function () {
    await this.player.claim(this.alice, this.otherWithFee);
    await expectRevert(
      this.player.claim(this.alice, this.ownerWithFee),
      'Name taken.',
    );
  });
});