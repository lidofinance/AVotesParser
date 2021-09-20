"""Tests of getting ABI from different sources."""
import os
from collections import namedtuple

import pytest

from evmscript_parser.core.ABI import get_cached_combined
from evmscript_parser.core.ABI.storage import CachedStorage, ABIKey
from evmscript_parser.core.decode import decode_function_call

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
INTERFACES = os.path.join(CUR_DIR, 'interfaces')

FunctionCall = namedtuple(
    'FunctionCall',
    field_names=['address', 'signature', 'name', 'call_data'],
)

positive_examples = (
    # Tether
    FunctionCall(
        address='0xdac17f958d2ee523a2206206994597c13d831ec7',
        signature='0x18160ddd',
        name='totalSupply',
        call_data=''
    ),
    # Lido
    FunctionCall(
        address='0xae7ab96520de3a18e5e111b5eaab095312d7fe84',
        signature='0x18160ddd',
        name='totalSupply',
        call_data=''
    )
)


@pytest.fixture(scope='module', params=positive_examples)
def positive_example(request):
    """Get positive test case for call decoding."""
    return request.param


@pytest.fixture(scope='module')
def abi_storage(api_key: str) -> CachedStorage:
    """Return prepared abi storage."""
    return get_cached_combined(
        api_key, 'goerli', INTERFACES
    )


def test_etherscan_api(abi_storage, positive_example: FunctionCall):
    """Run tests for getting ABI from Etherscan API."""
    assert decode_function_call(
        positive_example.address, positive_example.signature,
        positive_example.call_data, abi_storage
    ).function_name == positive_example.name
    assert ABIKey(
        positive_example.address, positive_example.signature
    ) in abi_storage
