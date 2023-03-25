pragma solidity >=0.8.0;

// SPDX-License-Identifier: AGPL-3.0-or-later

contract SingleShotFaucetStorage {
	// Implements EIP 173
	address public owner;
	address newOwner;

	mapping (address => uint256) usedAccounts;
	address[] public entry;

	// Implements EIP 173
	event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

	// Implements AccountsIndex
	event AddressAdded(uint256 indexed accountIndex, address _account); // AccountsIndex

	// Implements AccountsIndex
	uint256 constant public time = 0;

	constructor() {
		owner = msg.sender;
		entry.push(address(0));
		usedAccounts[address(0)] = 1;
	}

	// Implements EIP 173
	function transferOwnership(address _newOwner) external {
		address _oldOwner;

		require(msg.sender == owner);
		_oldOwner = owner;

		owner = _newOwner;

		emit OwnershipTransferred(_oldOwner, owner);
	}

	// Implements AccountsIndex
	function have(address _account) external view returns (bool) {
		return usedAccounts[_account] > 0;
	}

	// Implements AccountsIndex
	function add(address _account) external returns (bool) {
		require(msg.sender == owner, 'ERR_AXX');

		uint256 l;

		l = entry.length;
		entry.push(_account);
		usedAccounts[_account] = l;
		emit AddressAdded(l, _account);
		return true;
	}

	// Implements EIP165
	function supportsInterface(bytes4 _sum) public pure returns (bool) {
		if (_sum == 0xb7bca625) { // AccountsIndex
			return true;
		}
		if (_sum == 0x01ffc9a7) { // EIP165
			return true;
		}
		if (_sum == 0x9493f8b2) { // EIP173
			return true;
		}
		return false;
	}
}
