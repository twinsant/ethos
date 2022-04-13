// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.7;

import "@openzeppelin/contracts/access/Ownable.sol";

contract Player is Ownable {
  mapping (address => string) public names;
  mapping (string => address) public whois;
  
  constructor() {
  }

  function whoami() public view returns (string memory) {
      return names[msg.sender];
  }

  function claim(string memory name)
    public payable
  {
      require(msg.value >= 0.01 ether, "0.01 Ethers needed.");
      
      if (whois[name] == address(0)) {
        names[msg.sender] = name;
        whois[name] = msg.sender;
      } else {
          if (whois[name] == msg.sender ) {
              names[msg.sender] = name;
          } else {
              revert("Name taken.");
          }
      }
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