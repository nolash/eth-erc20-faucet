FROM grassrootseconomics:bancor

ARG pip_extra_index_url=https://pip.grassrootseconomics.net:8433

COPY ./python/ ./erc20-single-shot-faucet

RUN cd erc20-single-shot-faucet && \
	pip install --extra-index-url $pip_extra_index_url .

