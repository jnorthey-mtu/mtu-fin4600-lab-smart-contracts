// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract SimpleStorage {
    uint256 public storedRate;  // anyone can read it

    event RateChanged(address by, uint256 newRate);

    function setRate(uint256 newRate) external {
        storedRate = newRate;   // a write: costs gas
        emit RateChanged(msg.sender, newRate);
    }
}
