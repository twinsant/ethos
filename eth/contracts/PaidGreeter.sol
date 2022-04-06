//SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.0;

import "hardhat/console.sol";

contract PaidGreeter {
    address payable public owner;

    string private greeting;

    constructor(string memory _greeting) {
        owner = payable(msg.sender);

        console.log("Deploying a Greeter with greeting:", _greeting);
        greeting = _greeting;
    }

    function greet() public view returns (string memory) {
        return greeting;
    }

    // https://solidity-by-example.org/payable/
    function setGreeting(string memory _greeting) public payable {
        require(msg.value >= 0.01 ether, "0.01 Ethers needed.");
        console.log("Changing greeting from '%s' to '%s'", greeting, _greeting);
        greeting = _greeting;
    }

    function withdraw() public {
        // get the amount of Ether stored in this contract
        uint amount = address(this).balance;

        // send all Ether to owner
        // Owner can receive Ether since the address of owner is payable
        (bool success, ) = owner.call{value: amount}("");
        require(success, "Failed to send Ether");
    }
}
