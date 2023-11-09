from collections import namedtuple

import pytest

from avotes_parser.core import parse_script, EVMScript
from avotes_parser.core.ABI.provider import get_cached_etherscan_api
from avotes_parser.core.decoding import FuncInput, Call

ParsingTestCase = namedtuple(
    'ParsingTestCase', field_names=['raw_script', 'parsed_script']
)

parse_with_decoding_examples = (
    ParsingTestCase(
        raw_script="0x000000019d4af1ee19dad8857db3a45b0374c81c8a1c632000000044"
                   "ae962acf00000000000000000000000000000000000000000000000000"
                   "0000000000000c00000000000000000000000000000000000000000000"
                   "0000000000000000001d",
        parsed_script=EVMScript(
            spec_id='00000001',
            calls=[
                Call(
                    contract_address="0x9d4af1ee19dad8857db3a45b0374c81c8a1c6320", # noqa
                    function_signature="0xae962acf",
                    function_name="setNodeOperatorStakingLimit",
                    inputs=[
                        FuncInput(
                            name="_id",
                            type="uint256",
                            value=12,
                        ),
                        FuncInput(
                            name="_stakingLimit",
                            type="uint64",
                            value=29,
                        ),
                    ],
                    properties=dict(),
                    outputs=list(),
                )
            ]
        )
    ),
)


@pytest.fixture(scope='module', params=parse_with_decoding_examples)
def parse_with_decoding_example(request):
    """Get positive test case for parsing with encoding of calls."""
    return request.param.raw_script, request.param.parsed_script


@pytest.fixture(scope='module')
def abi_storage(api_key: str, target_net: str):
    """Return prepared abi storage."""
    return get_cached_etherscan_api(api_key=api_key, net=target_net)


def test_parse_with_call_decoding(abi_storage, parse_with_decoding_example):
    """Run tests for positive parsing examples with encoding of calls."""
    script_code, prepared = parse_with_decoding_example
    parsed = parse_script(script_code, abi_storage)

    assert parsed.spec_id == prepared.spec_id
    assert len(prepared.calls) == len(parsed.calls)

    for prepared_call, parsed_call in zip(
            prepared.calls, parsed.calls
    ):
        assert parsed_call.contract_address == prepared_call.contract_address
        assert parsed_call.function_signature == \
            prepared_call.function_signature
        assert parsed_call.function_name == prepared_call.function_name

        for prepared_call.input, parsed_call.input in zip(
            prepared_call.inputs, parsed_call.inputs
        ):
            assert parsed_call.input.name == prepared_call.input.name
            assert parsed_call.input.type == prepared_call.input.type
            assert parsed_call.input.value == prepared_call.input.value
