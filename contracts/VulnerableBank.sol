// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

// A tiny bank with the same bug that drained The DAO in 2016.
contract VulnerableBank {
    mapping(address => uint256) public balanceOf;

    function deposit() external payable {
        balanceOf[msg.sender] += msg.value;
    }

    function withdraw() external {
        uint256 amount = balanceOf[msg.sender];
        require(amount > 0, "nothing to withdraw");
        (bool ok, ) = msg.sender.call{value: amount}("");  // 1. send the money...
        require(ok, "send failed");
        balanceOf[msg.sender] = 0;                         // 2. ...then update the books (too late!)
    }
}
