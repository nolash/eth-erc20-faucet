pragma solidity >=0.6.21;

// SPDX-License-Identifier: GPL-3.0-or-later

interface ISingleShotFaucetStorage {
	function transferOwnership(address) external returns(bool);
	function completeOwnership() external returns(bool);
	function add(address) external returns(bool);
	function have(address) external returns(bool);
}
