SOLC = /usr/bin/solc

all:
	$(SOLC) --bin ERC20FaucetStorage.sol --evm-version byzantium | awk 'NR>3' > ERC20FaucetStorage.bin
	truncate -s -1 ERC20FaucetStorage.bin
	$(SOLC) --abi ERC20FaucetStorage.sol --evm-version byzantium | awk 'NR>3' > ERC20FaucetStorage.json
	$(SOLC) --bin ERC20Faucet.sol --evm-version byzantium | awk 'NR>3' > ERC20Faucet.bin
	truncate -s -1 ERC20Faucet.bin
	$(SOLC) --abi ERC20Faucet.sol --evm-version byzantium | awk 'NR==4' > ERC20Faucet.json

install: all
	cp -v *{json,bin} ../python/erc20_faucet/data/

