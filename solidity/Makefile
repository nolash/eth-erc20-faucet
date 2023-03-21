SOLC = /usr/bin/solc

all:
	$(SOLC) --bin ERC20FaucetStorage.sol --evm-version byzantium | awk 'NR>3' > ERC20FaucetStorage.bin
	$(SOLC) --abi ERC20FaucetStorage.sol --evm-version byzantium | awk 'NR>3' > ERC20FaucetStorage.json
	$(SOLC) --metadata ERC20FaucetStorage.sol --evm-version byzantium | awk 'NR>3' > ERC20FaucetStorage.metadata.json
	$(SOLC) --bin ERC20Faucet.sol --evm-version byzantium | awk 'NR>3' > ERC20Faucet.bin
	$(SOLC) --abi ERC20Faucet.sol --evm-version byzantium | awk 'NR==4' > ERC20Faucet.json
	$(SOLC) --metadata ERC20Faucet.sol --evm-version byzantium | awk 'NR==4' > ERC20Faucet.metadata.json
	truncate -s -1 ERC20FaucetStorage.bin
	truncate -s -1 ERC20Faucet.bin

install: all
	cp -v *.json ../python/erc20_faucet/data/
	cp -v *.bin ../python/erc20_faucet/data/

