# AVotesParser

-----------------------------------------

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![python ~3.9](https://img.shields.io/badge/python->=3.8,<3.11-blue)
![poetry 1.2.2](https://img.shields.io/badge/poetry-1.2.2-blue)
[![Tests](https://github.com/lidofinance/AVotesParser/actions/workflows/github-actions.yml/badge.svg?branch=master)](https://github.com/lidofinance/AVotesParser/actions/workflows/github-actions.yml)
[![PyPi Core version](https://img.shields.io/pypi/v/avotes-parser-core?color=yellow&label=PyPI%3Aavotes-parser-core)](https://pypi.org/project/avotes-parser-core/)
[![PyPi CLI version](https://img.shields.io/pypi/v/avotes-parser-cli?color=yellow&label=PyPI%3Aavotes-parser-cli)](https://pypi.org/project/avotes-parser-cli/)


### About

CLI utility `avotes-parser` for parsing the last N running votes for target
aragon application. Utility is based on package `avotes-parser-core` for
parsing and
decoding [EVMScripts](https://hack.aragon.org/docs/aragonos-ref#evmscripts-1).

### 🏁 Getting started

- This project uses Brownie development framework. Learn more about [Brownie](https://eth-brownie.readthedocs.io/en/stable/index.html).
- [Poetry](https://python-poetry.org/) dependency and packaging manager is used to bootstrap environment and keep the repo sane.

### Prerequisites

- Python >= 3.8, <3.11
- Pip >= 20.0

### Installation

#### PyPi installation:

```shell
pip install --user avotes-parser-cli
```
alternatively, if you prefer `pipx`:
```shell
pipx install avotes-parser-cli
```

#### Installation from repository:

##### Step 1. Install Poetry

Use the following command to install poetry:

```shell
pip install --user poetry==1.2.2
```

alternatively, you could proceed with `pipx`:

```shell
pipx install poetry==1.2.2
```

##### Step 2. Install poetry dyn versioning plugin

The [poetry dynamic versioning](https://github.com/mtkennerly/poetry-dynamic-versioning) plugin allows synchronizing published PyPi versions with GitHub releases.

```shell
poetry self add "poetry-dynamic-versioning[plugin]"
```

##### Step 3. Build avotes-parser

```shell
git clone git@github.com:lidofinance/AVotesParser.git
cd AVotesParser

cd production/avotes-parser-core
poetry install

cd ../avotes-parser-cli
poetry install
```

### Usage

### `avotes-parser-cli` package

Notice: if you have chosen poetry install method then you should spawn poetry environment to proceed:
```shell
poetry shell
```

AVotesParser has the following command-line interface:

```shell
usage: avotes-parser [-h] --apitoken APITOKEN --infura INFURA [-n N] [--aragon-voting-address ARAGON_VOTING_ADDRESS] [--net {mainnet,goerli,kovan,rinkebay,ropsten}] [--retries RETRIES] [--num-workers NUM_WORKERS] [--debug]

Parsing and decoding aragon votes. Prepare human-readable representation of the last N votes for a aragon application with a specific address in a target net.

optional arguments:
  -h, --help            show this help message and exit
  --apitoken APITOKEN   Etherscan API key as string or a path to txt file with it. (default: None)
  --infura INFURA       Infura project ID. (default: None)
  -n N                  Parse last N votes. (default: 10)
  --aragon-voting-address ARAGON_VOTING_ADDRESS
                        Address of aragon voting contract. (default: 0x2e59A20f205bB85a89C53f1936454680651E618e)
  --net {mainnet,goerli,kovan,rinkebay,ropsten}
                        Net name is case-insensitive. (default: mainnet)
  --retries RETRIES     Number of retries of calling Etherscan API. (default: 5)
  --num-workers NUM_WORKERS
                        Number of asynchronous parsing tasks. (default: 10)
  --debug               Show debug messages (default: False)
```

Example of running for the last vote:

```shell
$ avotes-parser --infura $WEB3_INFURA_PROJECT_ID --apitoken $ETHERSCAN_API_TOKEN -n 1

Voting #90.
Point 1/4.
Function call
Contract: 0x55032650b14df07b85bf18a3a3ec8e0af2e028d5
Signature: 0xae962acf
Name: setNodeOperatorStakingLimit
Inputs:
_id: uint256 = 7
_stakingLimit: uint64 = 5000

...
```

Before using you should to make
your [Infura project](https://eth-brownie.readthedocs.io/en/stable/network-management.html#using-infura)
and to set its id value through `WEB3_INFURA_PROJECT_ID`. Also, you need to
create [Etherscan API token](https://docs.etherscan.io/getting-started/viewing-api-usage-statistics#creating-an-api-key)
.

### `avotes-parser-core` package

The core functionality of package is divided into the `parsing` and
the `decoding` parts. Parsing is a conversion from raw bytes string to the
prepared structure `EVMScript`. Parsing function:

```python
def parse_script(encoded_script: str) -> EVMScript:
    """
    Parse encoded EVM script.

    :param encoded_script: str, encoded EVM script.
    :return: parsed script as instance of EVMScript object.
    """
```

Located
in [`avotes_parser.core`](production/avotes-parser-core/avotes_parser/core/parsing.py)
sub-package.

For getting the sole decoded functions call should be
used `decode_function_call`
which is located
in [`avotes_parser.core`](production/avotes-parser-core/avotes_parser/core/decoding.py)
sub-package.

```python
def decode_function_call(
        contract_address: str, function_signature: str,
        call_data: str, abi_storage: _CacheT
) -> Optional[Call]:
    """
    Decode function call.

    :param contract_address: str, contract address.
    :param function_signature: str, the first fourth bytes
                                    of function signature
    :param call_data: str, encoded call data.
    :param abi_storage: CachedStorage, storage of contracts ABI.
    :return: Call, decoded description of function calling.
    """
```

`abi_storage` is the one of prepared cached abi storages:

- `CachedStorage` based on Etherscan API

```python
def get_cached_etherscan_api(
        api_key: str, net: str
) -> CachedStorage[ABIKey, ABI]:
    """
    Return prepared instance of CachedStorage with API provider.

    :param api_key: str, Etherscan API token.
    :param net: str, the name of target network.
    :return: CachedStorage[ABIKey, ABI]
    """
```

- `CachedStorage` based on local directory with interfaces files.

```python
def get_cached_local_interfaces(
        interfaces_directory: str
) -> CachedStorage[ABIKey, ABI]:
    """
    Return prepared instance of CachedStorage with local files provider.

    :param interfaces_directory: str, path to directory with interfaces.
    :return: CachedStorage[ABIKey, ABI]
    """
```

- `CachedStorage` based on combination of Etherscan API and local directory
  providers.

```python
def get_cached_combined(
        api_key: str, net: str,
        interfaces_directory: str
) -> CachedStorage[Tuple[ABIKey, ABIKey], ABI]:
    """
    Return prepared instance of CachedStorage with combined provider.

    :param api_key: str, Etherscan API token.
    :param net: str, the name of target network.
    :param interfaces_directory: str, path to directory with interfaces.
    :return: CachedStorage[ABIKey, ABI]
    """
```

All this function are located
in [`avotes_parser.core.ABI`](production/avotes-parser-core/avotes_parser/core/ABI/provider.py)
sub-package.

More detailed examples of package usage you can find in
[`utilities.py`](production/avotes-parser-cli/avotes_parser/cli/utilities.py)
of `avotes-parser` CLI tool.
