// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.7;

import "@openzeppelin/contracts/access/Ownable.sol";

contract Player is Ownable {
  mapping (address => string) public names;
  mapping (string => address) public whois;
  address public pendingOwner;
  event NameClaimed(address indexed player, string name);
  event Withdrawal(address indexed owner, uint256 amount);
  event OwnershipTransferStarted(address indexed owner, address indexed pendingOwner);
  
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
    require(msg.value == 0.01 ether, "Exact 0.01 ETH required.");
    bytes memory nameBytes = bytes(name);
    require(nameBytes.length > 0 && nameBytes.length <= 32, "Invalid name length.");
    for (uint256 i = 0; i < nameBytes.length; i++) {
        bytes1 character = nameBytes[i];
        require(
            (character >= 0x61 && character <= 0x7a) ||
            (character >= 0x30 && character <= 0x39) ||
            character == 0x5f,
            "Invalid name character."
        );
    }

    if (whois[name] != address(0) && whois[name] != msg.sender) {
        revert("Name taken.");
    }

    if (!_hashCompareWithLengthCheck("", names[msg.sender]) && _hashCompareWithLengthCheck(name, names[msg.sender])) {
        revert("Name already claimed.");
    }

    if (!_hashCompareWithLengthCheck("", names[msg.sender]) && whois[names[msg.sender]] != address(0)) {
        whois[names[msg.sender]] = address(0);
    }
     
    whois[name] = msg.sender;
    names[msg.sender] = name;
    emit NameClaimed(msg.sender, name);
  }

    function renounceOwnership() public pure override {
        revert("Ownership cannot be renounced.");
    }

    function transferOwnership(address newOwner) public override onlyOwner {
        require(newOwner != address(0), "Ownable: new owner is the zero address");
        pendingOwner = newOwner;
        emit OwnershipTransferStarted(owner(), newOwner);
    }

    function acceptOwnership() public {
        require(msg.sender == pendingOwner, "Not pending owner.");
        delete pendingOwner;
        _transferOwnership(msg.sender);
    }

    function withdraw() public onlyOwner {
        // get the amount of Ether stored in this contract
        uint amount = address(this).balance;
        require(amount > 0 ether, "Balance zero!");

        // send all Ether to owner
        // Owner can receive Ether since the address of owner is payable
        (bool success, ) = owner().call{value: amount}("");
        require(success, "Failed to send Ether");
        emit Withdrawal(owner(), amount);
    }
}

// (base) ➜  eth git:(main) ✗ hh --network localhost deploy --contract Player