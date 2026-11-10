// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract ClassToken {
    string public name = "Husky Dollar";
    address public issuer;
    mapping(address => uint256) public balanceOf;
    mapping(address => bool) public frozen;

    constructor(uint256 supply) {
        issuer = msg.sender;
        balanceOf[msg.sender] = supply;
    }

    function transfer(address to, uint256 amount) external {
        require(!frozen[msg.sender], "account frozen");
        require(balanceOf[msg.sender] >= amount, "insufficient balance");
        balanceOf[msg.sender] -= amount;
        balanceOf[to] += amount;
    }

    function freeze(address account) external {
        require(msg.sender == issuer, "only issuer");
        frozen[account] = true;
    }
}
