pragma solidity >0.6.11;

// SPDX-License-Identifier: GPL-3.0-or-later

contract SingleShotFaucet {

	address owner;
	mapping( address => bool) overriders; // TODO replace with writers
	// Implements Faucet
	uint256 public tokenAmount;
	// Implements Faucet
	address public token;
	address store;
	address accountsIndex;
	mapping(address => bool) writers;
	uint256 cooldownDisabled;

	event Give(address indexed _recipient, address indexed _token, uint256 _value);
	event FaucetAmountChange(uint256 _value);

	constructor(address[] memory _overriders, address _token, address _store, address _accountsIndex) {
		owner = msg.sender;
		overriders[msg.sender] = true;
		for (uint i = 0; i < _overriders.length; i++) {
			overriders[_overriders[i]] = true;
		}
		store = _store;
		token = _token;
		accountsIndex = _accountsIndex;
		cooldownDisabled = uint256(0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff);
	}

	// Implements Faucet
	function setAmount(uint256 _amount) public returns (bool) {
		require(overriders[msg.sender]);
		tokenAmount = _amount;
		emit FaucetAmountChange(_amount);
		return true;
	}

	// Implements Faucet
	function giveTo(address _recipient) public returns (uint256) {
		require(!overriders[_recipient], 'ERR_ACCESS');
	
		bool _ok;
		bytes memory _result;

		if (accountsIndex != address(0)) {	
			(_ok,  _result) = accountsIndex.call(abi.encodeWithSignature("have(address)", _recipient));
			require(_result[31] != 0, 'ERR_ACCOUNT_NOT_IN_INDEX');
		}

		(_ok, _result) = store.call(abi.encodeWithSignature("have(address)", _recipient));
		
		require(_result[31] == 0, 'ERR_ACCOUNT_USED'); // less conversion than: // require(abi.decode(_result, (bool)) == false, 'ERR_ACCOUNT_USED');

		//(_ok, _result) = store.call(abi.encodeWithSignature("lock(address)", _recipient));
		(_ok, _result) = store.call(abi.encodeWithSignature("add(address)", _recipient));
		require(_ok, 'ERR_MARK_FAIL');

		(_ok, _result) = token.call(abi.encodeWithSignature("transfer(address,uint256)", _recipient, tokenAmount));
		if (!_ok) {
			revert('ERR_TRANSFER');
		}
			
		emit Give(_recipient, token, tokenAmount);
		return tokenAmount;
	}

	function gimme() public returns (uint256) {
		return giveTo(msg.sender);
	}

	// Implements Faucet
	function nextTime(address _recipient) public returns (uint256) {
		bool _ok;
		bytes memory _result;

		(_ok, _result) = store.call(abi.encodeWithSignature("have(address)", _recipient));

		require(_ok, 'ERR_STORE_FAIL');

		if (_result[31] == 0x01) {
			return cooldownDisabled;
		} else {
			return 0;
		}
	}

	// Implements Writer
	function addWriter(address _writer) public returns (bool) {
		require(owner == msg.sender);
		writers[_writer] = true;
		return true;
	}

	// Implements Writer
	function deleteWriter(address _writer) public returns (bool) {
		require(owner == msg.sender);
		delete writers[_writer];
		return true;
	}

	// Implements EIP165
	function supportsInterface(bytes4 _sum) public pure returns (bool) {
		if (_sum == 0x01ffc9a7) { // EIP165
			return true;
		}
		if (_sum == 0xde344547) { // Faucet
			return true;
		}
		if (_sum == 0x80c84bd6) { // Writer
			return true;
		}
		return false;
	}
}
