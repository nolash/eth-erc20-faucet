pragma solidity >=0.8.0;

// SPDX-License-Identifier: AGPL-3.0-or-later

contract SingleShotFaucet {
	address public token;
	address store;
	address accountsIndex;
	uint256 constant cooldownDisabled = uint256(0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff);

	// Implements ERC173
	address public owner;

	// Implements Writer
	mapping( address => bool) public isWriter;

	// Implements Faucet
	uint256 public tokenAmount;

	// Implements Faucet
	event FaucetAmountChange(uint256 _value);

	// Implements Writer
	event WriterAdded(address _account);

	// Implements Writer
	event WriterDeleted(address _account);

	// Implements EIP 173
	event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

	constructor(address _token, address _store, address _accountsIndex) {
		owner = msg.sender;
		store = _store;
		token = _token;
		accountsIndex = _accountsIndex;
	}

	// Implements Writer
	function addWriter(address _address) public returns(bool) {
		require(msg.sender == owner, 'ERR_AXX');
		isWriter[_address] = true;
		emit WriterAdded(_address);
		return true;
	}

	// Implements Writer
	function deleteWriter(address _address) public returns(bool) {
		require(msg.sender == owner || msg.sender == _address, 'ERR_AXX');
		isWriter[_address] = false;
		emit WriterDeleted(_address);
		return true;
	}

	// Change faucet amount
	function setAmount(uint256 _amount) public returns (bool) {
		require(isWriter[msg.sender] || msg.sender == owner);
		tokenAmount = _amount;
		emit  FaucetAmountChange(_amount);
		return true;
	}

	// Implements Faucet
	function giveTo(address _recipient) public returns (uint256) {
		bool _ok;
		bytes memory _result;

		if (accountsIndex != address(0)) {	
			(_ok,  _result) = accountsIndex.call(abi.encodeWithSignature("have(address)", _recipient));
			require(_result[31] != 0, 'ERR_ACCOUNT_NOT_IN_INDEX');
		}

		(_ok, _result) = store.call(abi.encodeWithSignature("have(address)", _recipient));
		
		require(_result[31] == 0, 'ERR_ACCOUNT_USED');
		(_ok, _result) = store.call(abi.encodeWithSignature("add(address)", _recipient));
		require(_ok, 'ERR_MARK_FAIL');

		(_ok, _result) = token.call(abi.encodeWithSignature("transfer(address,uint256)", _recipient, tokenAmount));
		if (!_ok) {
			revert('ERR_TRANSFER');
		}
			
		return tokenAmount;
	}

	// Implements Faucet
	function gimme() public returns (uint256) {
		return giveTo(msg.sender);
	}

	// Implements Faucet
	function check(address _recipient) public returns (bool) {
		bool _ok;
		bytes memory _result;

		(_ok, _result) = store.call(abi.encodeWithSignature("have(address)", _recipient));

		require(_ok, 'ERR_STORE_FAIL');
		
		return _result[31] == 0x00;
	}

	// Implements Faucet
	function nextTime(address _recipient) public returns (uint256) {
		bool _ok;
		bytes memory _result;

		(_ok, _result) = store.call(abi.encodeWithSignature("have(address)", _recipient));

		require(_ok, 'ERR_STORE_FAIL');

		if (_result[31] == 0x01) {
			return cooldownDisabled;
		}

		return 0;
	}

	// Implements Faucet
	function nextBalance(address _recipient) public pure returns (uint256) {
		_recipient;
		return 0;
	}

	// Implements EIP 173
	function transferOwnership(address _newOwner) external {
		address _oldOwner;

		require(msg.sender == owner);
		_oldOwner = owner;

		owner = _newOwner;

		emit OwnershipTransferred(_oldOwner, owner);
	}

	function supportsInterface(bytes4 _sum) public pure returns (bool) {
		if (_sum == 0x01ffc9a7) { // EIP165
			return true;
		}
		if (_sum == 0x1a3ac634) { // Faucet
			return true;
		}
		if (_sum == 0xabe1f1f5) { // Writer
			return true;
		}
		return false;
	}
}
