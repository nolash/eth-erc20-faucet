pragma solidity >=0.6.21;

// SPDX-License-Identifier: GPL-3.0-or-later

contract SingleShotFaucetStorage {
	address owner;
	address new_owner;

	mapping (address => bool) public used_accounts;

	constructor() public {
		owner = msg.sender;
	}

	function transferOwnership(address _new_owner) external returns (bool) {
		require(msg.sender == owner);
		new_owner = _new_owner;
		return true;
	}

	function completeOwnership() external returns (bool) {
		require(msg.sender == new_owner);
		owner = msg.sender;
		return true;
	}

	function lock(address _account) external returns (bool) {
		used_accounts[_account] = true;
		return true;
	}

	function isLocked(address _account) external view returns (bool) {
		return used_accounts[_account];
	}
}
