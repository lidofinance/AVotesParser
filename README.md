# EVMScriptParser

-----------------------------------------

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Tests](https://github.com/lidofinance/EVMScriptParser/actions/workflows/github-actions.yml/badge.svg?branch=master)](https://github.com/lidofinance/EVMScriptParser/actions/workflows/github-actions.yml)
[![PyPi version](https://pypip.in/v/evmscript-parser/badge.png)](https://crate.io/packages/evmscript-parser/)
[![PyPi downloads](https://pypip.in/d/evmscript-parser/badge.png)](https://crate.io/packages/evmscript-parser/)

### About

CLI utility `avotes-parser` for parsing the last N running votes on target
aragon application. Utility is based on package `evmscript_parser` for 
parsing and decoding [EVMScripts](https://hack.aragon.org/docs/aragonos-ref#evmscripts-1).

### Installation

1. From PyPi:

```shell
pip install evmscript-parser
```

2. From repository:

```shell
git clone https://github.com/DmitIv/EVMScriptParser.git
cd EVMScriptParser
python setup.py install
```

### Usage

```shell
avotes-parser --help
usage: avotes-parser [-h] [-n N] [--net {mainnet,goerli,kovan,rinkebay,ropsten}] [--aragon-voting-address ARAGON_VOTING_ADDRESS] [--debug] [--retries RETRIES] apitoken

Observation for the last N running votes at the aragon voting.

positional arguments:
  apitoken              Etherscan API key as string or a path to txt file with it.

optional arguments:
  -h, --help            show this help message and exit
  -n N                  Parse last N votes.
  --net {mainnet,goerli,kovan,rinkebay,ropsten}
                        net name is case-insensitive, default is mainnet
  --aragon-voting-address ARAGON_VOTING_ADDRESS
                        Address of aragon voting contract
  --debug               Show debug messages
  --retries RETRIES     Number of retries of calling Etherscan API.
```

Example of running for the last vote:

```shell
$ WEB3_INFURA_PROJECT_ID=$WEB3_INFURA_PROJECT_ID avotes-parser $ETHERSCAN_API_KEY -n 1

Voting number 89.
Point 1/9
Contract: 0x3e40d73eb977dc6a537af587d48316fee66e9c8c
Function: forward
Inputs:
_evmScript: bytes = [
   Contract: 0x1dd909cddf3dbe61ac08112dc0fdf2ab949f79d8
   Function: set_rewards_limit_per_period
   Inputs:
   _new_limit: uint256 = 75000000000000000000000
]
...
```

Before using you should to make your [Infura project](https://eth-brownie.readthedocs.io/en/stable/network-management.html#using-infura) and to set its id value through `WEB3_INFURA_PROJECT_ID`.
Also, you need to create [Etherscan API token](https://docs.etherscan.io/getting-started/viewing-api-usage-statistics#creating-an-api-key).

### `evmscript_parser` package

The core functionality of package is divided into the `parsing` and the `decoding` parts. Parsing is a conversion from raw bytes string to the prepared structure `EVMScript`. 
Parsing function: 

```python
def parse_script(encoded_script: str) -> EVMScript:
    """
    Parse encoded EVM script.

    :param encoded_script: str, encoded EVM script.
    :return: parsed script as instance of EVMScript object.
    """
```

Located in [`evmscript_parser.core.parse`](evmscript_parser/core/parse/action.py) sub-package.

For getting the sole decoded functions call should be used `decode_function_call` 
which is located in [`evmscript_parser.core.decode`](evmscript_parser/core/decode/action.py) sub-package.

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

- `CachedStorage` based on combination of Etherscan API and local directory providers.
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

All this function are located in [`evmscript_parser.core.ABI`](evmscript_parser/core/ABI/provider.py) sub-package.

More detailed examples of package usage you can see in 
[`cli.py`](evmscript_parser/cli.py) and [`decoding.py`](evmscript_parser/core/decoding.py).
