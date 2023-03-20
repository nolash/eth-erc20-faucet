pragma solidity >0.6.11;

// SPDX-License-Identifier: GPL-3.0-or-later

contract SingleShotFaucetStorage {
	// Implements EIP 173
	address public owner;
	address newOwner;

	//mapping (address => bool) public usedAccounts;
	mapping (address => uint256) public usedAccounts;
	address[] public entry;

	// Implements EIP 173
	event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);
	event AddressAdded(address indexed addedAccount, uint256 indexed accountIndex); // AccountsIndex

	constructor() {
		owner = msg.sender;
		entry.push(address(0));
		usedAccounts[address(0)] = 0;
	}

	// Implements EIP 173
	function transferOwnership(address _newOwner) external {
		require(msg.sender == owner);
		newOwner = _newOwner;
	}

	// Implements OwnedAccepter
	function acceptOwnership() external returns (bool) {
		address previousOwner = owner;
		require(msg.sender == newOwner);
		owner = msg.sender;
		emit OwnershipTransferred(previousOwner, owner);
		return true;
	}

	// Implements AccountsIndex
	function have(address _account) external view returns (bool) {
		return usedAccounts[_account] > 0;
	}

	// Implements AccountsIndex
	function add(address _account) external returns (bool) {
		uint256 l;

		l = entry.length;
		entry.push(_account);
		usedAccounts[_account] = l;
		emit AddressAdded(_account, l);
		return true;
	}

	// Implements EIP165
	function supportsInterface(bytes4 _sum) public pure returns (bool) {
		if (_sum == 0xcbdb05c7) { // AccountsIndex
			return true;
		}
		if (_sum == 0x01ffc9a7) { // EIP165
			return true;
		}
		if (_sum == 0x9493f8b2) { // EIP173
			return true;
		}
		if (_sum == 0x37a47be4) { // OwnedAccepter
			return true;
		}
		return false;
	}
}
