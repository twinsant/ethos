// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.7;

import "@openzeppelin/contracts/access/Ownable.sol";
import "hardhat/console.sol";

contract Player is Ownable {
  mapping (address => string) public names; // TODO: handle case later
  mapping (string => address) public whois;
  
  constructor() {
  }

  function whoami() public view returns (string memory) {
      return names[msg.sender];
  }

    // https://fravoll.github.io/solidity-patterns/string_equality_comparison.html
  function _hashCompareWithLengthCheck(string memory a, string memory b) internal pure returns (bool) {
      bytes memory _a = bytes(a);
      bytes memory _b = bytes(b);
    if(_a.length != _b.length) {
        return false;
    } else {
        return keccak256(_a) == keccak256(_b);
    }
}

  function claim(string memory name)
    public payable {
    require(msg.value >= 0.01 ether, "0.01 Ethers needed.");
    require(!_hashCompareWithLengthCheck(name, ""), "Empty string not allowed.");
    // TODO: check not allowed chars

    if (whois[name] != address(0) && whois[name] != msg.sender) {
        revert("Name taken.");
    }

    if (!_hashCompareWithLengthCheck("", names[msg.sender]) && _hashCompareWithLengthCheck(name, names[msg.sender])) {
        return;
    }

    if (!_hashCompareWithLengthCheck("", names[msg.sender]) && whois[names[msg.sender]] != address(0)) {
        whois[names[msg.sender]] = address(0);
    }
     
    whois[name] = msg.sender;
    names[msg.sender] = name;
  }

    function withdraw() public onlyOwner {
        // get the amount of Ether stored in this contract
        uint amount = address(this).balance;
        require(amount > 0 ether, "Balance zero!");

        // send all Ether to owner
        // Owner can receive Ether since the address of owner is payable
        (bool success, ) = owner().call{value: amount}("");
        require(success, "Failed to send Ether");
    }
}

// (base) ➜  eth git:(main) ✗ hh --network localhost deploy --contract Player