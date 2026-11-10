// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract Escrow {
    address public buyer;
    address payable public seller;
    uint256 public deadline;
    bool public settled;

    constructor(address payable _seller, uint256 daysToDeliver) payable {
        require(msg.value > 0, "deposit required");
        buyer = msg.sender;
        seller = _seller;
        deadline = block.timestamp + daysToDeliver * 1 days;
    }

    function confirmDelivery() external {
        require(msg.sender == buyer, "only buyer");
        require(!settled, "already settled");
        settled = true;                    // effects before interaction
        (bool ok, ) = seller.call{value: address(this).balance}("");
        require(ok, "payment failed");
    }

    function refund() external {
        require(msg.sender == buyer, "only buyer");
        require(!settled, "already settled");
        require(block.timestamp > deadline, "too early");
        settled = true;
        (bool ok, ) = payable(buyer).call{value: address(this).balance}("");
        require(ok, "refund failed");
    }
}
