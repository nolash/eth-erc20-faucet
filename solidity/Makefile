all:
	solc --bin ERC20SingleShotFaucetStorage.sol | awk 'NR>3' > ERC20SingleShotFaucetStorage.bin
	truncate -s -1 ERC20SingleShotFaucetStorage.bin
	solc --abi ERC20SingleShotFaucetStorage.sol | awk 'NR>3' > ERC20SingleShotFaucetStorage.json
	solc --bin ERC20SingleShotFaucet.sol | awk 'NR>3' > ERC20SingleShotFaucet.bin
	truncate -s -1 ERC20SingleShotFaucet.bin
	solc --abi ERC20SingleShotFaucet.sol | awk 'NR==4' > ERC20SingleShotFaucet.json
	#solc --abi IERC20SingleShotFaucetStorage.sol | awk 'NR>3' > IERC20SingleShotFaucetStorage.abi.json

install: all
	cp -v *{json,bin} ../python/erc20_single_shot_faucet/data/

