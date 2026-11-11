const { expectRevert } = require('@openzeppelin/test-helpers');
const { assert } = require('chai');
const TemporalLoot = artifacts.require('TemporalLoot');

contract('TemporalLoot', function ([owner]) {
  it('only serves metadata for minted tokens, including token zero', async function () {
    const loot = await TemporalLoot.new({ from: owner });
    await expectRevert(loot.tokenURI(0), 'ERC721Metadata: URI query for nonexistent token');
    await loot.claim(0, { from: owner });
    assert.isTrue((await loot.tokenURI(0)).startsWith('data:application/json;base64,'));
    await expectRevert(loot.tokenURI(1), 'ERC721Metadata: URI query for nonexistent token');
  });
});
