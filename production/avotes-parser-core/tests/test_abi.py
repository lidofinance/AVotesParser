"""Tests of getting ABI from different sources."""
import os
from collections import namedtuple

import pytest

from avotes_parser.core import decode_function_call
from avotes_parser.core.ABI import get_cached_combined
from avotes_parser.core.ABI.storage import CachedStorage, ABIKey

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
INTERFACES = os.path.join(CUR_DIR, 'interfaces')

FunctionCall = namedtuple(
    'FunctionCall',
    field_names=['address', 'signature', 'name', 'call_data', 'was'],
)

positive_examples = (
    # Tether
    FunctionCall(
        address='0xdac17f958d2ee523a2206206994597c13d831ec7',
        signature='0x18160ddd',
        name='totalSupply',
        call_data='',
        was=False
    ),
    # Lido
    FunctionCall(
        address='0xae7ab96520de3a18e5e111b5eaab095312d7fe84',
        signature='0x18160ddd',
        name='totalSupply',
        call_data='',
        was=False
    ),
    # Lido finance address
    FunctionCall(
        address='0x75c7b1D23f1cad7Fb4D60281d7069E46440BC179',
        signature='0x33ea3dc8',
        name='getTransaction',
        call_data='1'.zfill(64),
        was=False
    ),
    # Lido, second call
    FunctionCall(
        address='0xae7ab96520de3a18e5e111b5eaab095312d7fe84',
        signature='0x18160ddd',
        name='totalSupply',
        call_data='',
        was=True
    ),
    # Lido, wrong address, target signature not in ABI
    FunctionCall(
        address='0x75c7b1D23f1cad7Fb4D60281d7069E46440BC179',
        signature='0x18160ddd',
        name=None,
        call_data='',
        was=False
    ),
    # Lido node operator registry
    FunctionCall(
        address='0x9D4AF1Ee19Dad8857db3a45B0374c81c8A1C6320',
        signature='0x62dcfda1',
        name='getRewardsDistribution',
        call_data='1'.zfill(64),
        was=False
    )
)


@pytest.fixture(
    scope='module', params=positive_examples,
    ids=lambda x: f'{x.address}:{x.signature}'
)
def positive_example(request):
    """Get positive test case for call decoding."""
    return request.param


@pytest.fixture(scope='module')
def abi_storage(
        api_key: str, infura_prt_id: str, target_net: str
) -> CachedStorage:
    """Return prepared abi storage."""
    return get_cached_combined(
        api_key, target_net, INTERFACES
    )


def test_combined_storage(abi_storage):
    """Run tests for prepared combined storage."""
    interfaces = abi_storage._provider._interfaces
    assert len(interfaces) > 0
    assert '0x18160ddd' in interfaces
    assert '0x35390714' in interfaces
    assert '0x62dcfda1' in interfaces


def test_etherscan_api(abi_storage, positive_example: FunctionCall):
    """Run tests for getting ABI from Etherscan API."""
    key = ABIKey(positive_example.address, positive_example.signature)
    assert (key in abi_storage) is positive_example.was
    decoded = decode_function_call(
        positive_example.address, positive_example.signature,
        positive_example.call_data, abi_storage,
    )
    if positive_example.name:
        assert decoded.function_name == positive_example.name
    else:
        assert decoded is None
    assert key in abi_storage
