pragma solidity >0.6.11;

// SPDX-License-Identifier: GPL-3.0-or-later

contract SingleShotFaucetStorage {
	// EIP 173
	address public owner;
	address newOwner;

	mapping (address => bool) public usedAccounts;

	// EIP 173
	event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

	constructor() public {
		owner = msg.sender;
	}

	// EIP 173
	function transferOwnership(address _newOwner) external {
		require(msg.sender == owner);
		newOwner = _newOwner;
	}

	function acceptOwnership() external returns (bool) {
		address previousOwner = owner;
		require(msg.sender == newOwner);
		owner = msg.sender;
		emit OwnershipTransferred(previousOwner, owner);
		return true;
	}

	function add(address _account) external returns (bool) {
		usedAccounts[_account] = true;
		return true;
	}

	function have(address _account) external view returns (bool) {
		return usedAccounts[_account];
	}
}
