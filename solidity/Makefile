SOLC = /usr/bin/solc

all:
	$(SOLC) --bin ERC20SingleShotFaucetStorage.sol --evm-version byzantium | awk 'NR>3' > ERC20SingleShotFaucetStorage.bin
	truncate -s -1 ERC20SingleShotFaucetStorage.bin
	$(SOLC) --abi ERC20SingleShotFaucetStorage.sol --evm-version byzantium | awk 'NR>3' > ERC20SingleShotFaucetStorage.json
	$(SOLC) --bin ERC20SingleShotFaucet.sol --evm-version byzantium | awk 'NR>3' > ERC20SingleShotFaucet.bin
	truncate -s -1 ERC20SingleShotFaucet.bin
	$(SOLC) --abi ERC20SingleShotFaucet.sol --evm-version byzantium | awk 'NR==4' > ERC20SingleShotFaucet.json

install: all
	cp -v *{json,bin} ../python/erc20_single_shot_faucet/data/

