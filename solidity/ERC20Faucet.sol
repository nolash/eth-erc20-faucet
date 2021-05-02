pragma solidity >0.6.11;

// SPDX-License-Identifier: GPL-3.0-or-later

contract SingleShotFaucet {

	address owner;
	mapping( address => bool) overriders;
	uint256 public amount;
	address public token;
	address store;
	address accountsIndex;
	uint256 cooldownDisabled;

	event FaucetUsed(address indexed _recipient, address indexed _token, uint256 _value);
	event FaucetFail(address indexed _recipient, address indexed _token, uint256 _value);
	event FaucetAmountChange(uint256 _value);

	constructor(address[] memory _overriders, address _token, address _store, address _accountsIndex) public {
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

	function setAmount(uint256 _amount) public returns (bool) {
		require(overriders[msg.sender]);
		amount = _amount;
		emit  FaucetAmountChange(_amount);
		return true;
	}

	function giveTo(address _recipient) public returns (bool) {
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

		(_ok, _result) = token.call(abi.encodeWithSignature("transfer(address,uint256)", _recipient, amount));
		if (!_ok) {
			emit FaucetFail(_recipient, token, amount);
			revert('ERR_TRANSFER');
		}
			
		emit FaucetUsed(_recipient, token, amount);
		return true;
	}

	function cooldown(address _recipient) public returns (uint256) {
		bool _ok;
		bytes memory _result;

		(_ok, _result) = store.call(abi.encodeWithSignature("have(address)", _recipient));
		if (_ok) {
			return cooldownDisabled;
		} else {
			return 0;
		}
	}

	function tokenAmount() public view returns (uint256) {
		return amount;
	}
}
