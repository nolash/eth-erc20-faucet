pragma solidity >=0.6.21;

// SPDX-License-Identifier: GPL-3.0-or-later

contract SingleShotFaucet {

	address owner;
	mapping( address => bool) overriders;
	uint256 public amount;
	address public token;
	address store;

	event FaucetUsed(address indexed _recipient, address indexed _token, uint256 _value);
	event FaucetFail(address indexed _recipient, address indexed _token, uint256 _value);

	constructor(address[] memory _overriders, address _token, address _store) public {
		owner = msg.sender;
		overriders[msg.sender] = true;
		for (uint i = 0; i < _overriders.length; i++) {
			overriders[_overriders[i]] = true;
		}
		store = _store;
		token = _token;
	}

	function setAmount(uint256 _amount) public returns (bool) {
		require(overriders[msg.sender]);
		amount = _amount;
		return true;
	}

	function giveTo(address _recipient) public returns (bool) {
		require(!overriders[_recipient], 'ERR_ACCESS');
		(bool _ok, bytes memory _result) = store.call(abi.encodeWithSignature("isLocked(address)", _recipient));
		
		require(_result[31] == 0, 'ERR_ACCOUNT_USED'); // less conversion than: // require(abi.decode(_result, (bool)) == false, 'ERR_ACCOUNT_USED');

		(_ok, _result) = store.call(abi.encodeWithSignature("lock(address)", _recipient));
		require(_ok, 'ERR_MARK_FAIL');

		(_ok, _result) = token.call(abi.encodeWithSignature("transfer(address,uint256)", _recipient, amount));
		if (!_ok) {
			emit FaucetFail(_recipient, token, amount);
			revert('ERR_TRANSFER');
		}
			
		emit FaucetUsed(_recipient, token, amount);
		return true;
	}
}
