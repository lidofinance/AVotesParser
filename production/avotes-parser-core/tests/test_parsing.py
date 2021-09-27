"""Tests for EVMScripts parser"""
from collections import namedtuple

import pytest

from avotes_parser.core import parse_script, EVMScript, EncodedCall
from avotes_parser.core.parsing import ParseMismatchLength
from avotes_parser.core.spec import HEX_PREFIX

ParsingTestCase = namedtuple(
    'ParsingTestCase', field_names=['raw_script', 'parsed_script']
)


def test_single_parsing():
    """Perform simple test for the single EVM script."""
    spec_id = '00000001'
    address = '7804b6667d649c819dfa94af50c782c26f5abc32'
    method_id = '945233e2'
    call_data = '000000000000000000000000922' \
                'c10dafffb8b9be4c40d3829c8c708a12827f3'  # noqa
    call_data_length_int = (len(method_id) + len(call_data)) // 2
    call_data_length = hex(call_data_length_int)[2:].zfill(8)

    parsed_script = parse_script(''.join((
        HEX_PREFIX,
        spec_id, address, call_data_length,
        method_id, call_data
    )))

    def _with_prefix(data: str) -> str:
        return f'{HEX_PREFIX}{data}'

    assert parsed_script.spec_id == _with_prefix(spec_id)
    for ind, one_call in enumerate(parsed_script.calls):
        assert one_call.address == _with_prefix(address), ind
        assert one_call.call_data_length == call_data_length_int, ind
        assert one_call.method_id == _with_prefix(method_id), ind
        assert one_call.encoded_call_data == _with_prefix(call_data), ind


positive_examples = (
    ParsingTestCase(
        raw_script='0x000000017899ef901ed9b331baf7759'
                   'c15d2e8728e8c2a2c00000044ae962acf'
                   '000000000000000000000000000000000'
                   '000000000000000000000000000000100'
                   '000000000000000000000000000000000'
                   '000000000000000000000000000c9',
        parsed_script=EVMScript(
            spec_id='00000001',
            calls=[
                EncodedCall(
                    address='7899ef901ed9b331baf7759c15d2e8728e8c2a2c',
                    call_data_length=68,
                    method_id='ae962acf',
                    encoded_call_data=(
                        '000000000000000000000000000000000000'
                        '000000000000000000000000000100000000'
                        '000000000000000000000000000000000000'
                        '000000000000000000c9'
                    )
                )
            ]
        )
    ),
    ParsingTestCase(
        raw_script='0x00000001'
                   '8EcF1A208E79B300C33895B'
                   '62462ffb5b55627E500000024945233e2'
                   '000000000000000000000000922c10daf'
                   'ffb8b9be4c40d3829c8c708a12827f3'
                   '8EcF1A208E79B300C33895B'
                   '62462ffb5b55627E500000024945233e2'
                   '000000000000000000000000922c10daf'
                   'ffb8b9be4c40d3829c8c708a12827f3',
        parsed_script=EVMScript(
            spec_id='00000001',
            calls=[
                EncodedCall(
                    address='8EcF1A208E79B300C33895B62462ffb5b55627E5',
                    call_data_length=36,
                    method_id='945233e2',
                    encoded_call_data=(
                        '000000000000000000000000'
                        '922c10dafffb8b9be4c40d38'
                        '29c8c708a12827f3'
                    )
                ),
                EncodedCall(
                    address='8EcF1A208E79B300C33895B62462ffb5b55627E5',
                    call_data_length=36,
                    method_id='945233e2',
                    encoded_call_data=(
                        '000000000000000000000000'
                        '922c10dafffb8b9be4c40d38'
                        '29c8c708a12827f3'
                    )
                )
            ]
        )
    ),
    ParsingTestCase(
        raw_script='0x0000000107804b6667d649c819dfa94a'
                   'f50c782c26f5abc300000024945233e200'
                   '0000000000000000000000922c10dafffb'
                   '8b9be4c40d3829c8c708a12827f3',
        parsed_script=EVMScript(
            spec_id='00000001',
            calls=[
                EncodedCall(
                    address='07804b6667d649c819dfa94af50c782c26f5abc3',
                    call_data_length=36,
                    method_id='945233e2',
                    encoded_call_data=(
                        '000000000000000000000000922c10'
                        'dafffb8b9be4c40d3829c8c708a128'
                        '27f3'
                    )
                )
            ]
        )
    ),
    ParsingTestCase(
        raw_script='0x00000001'
                   '07804b6667d649c819dfa94af50c782c26f5abc3'
                   '00000108'
                   'f153cc32'
                   '730534100000000000000000000000000'
                   '00000000000000000000000000000000000'
                   '00020000000000000000000000000000000'
                   '00000000000000000000000000000000000'
                   '00000000000000000000000000000000000'
                   '00000000000000000000000000000000000'
                   '0000000000000000fd5952ef8de4707f95e'
                   '754299e8c0ffd1e876f3400000000000000'
                   '00000000000000000000000000000000000'
                   '0000000000000a000000000000000000000'
                   '00000000000000000000000000000000000'
                   '000000033697066733a516d596277436637'
                   '4d6e6932797a31553358334769485667396'
                   'f35316a6b53586731533877433257547755'
                   '68485900000000000000000000000000',
        parsed_script=EVMScript(
            spec_id='00000001',
            calls=[
                EncodedCall(
                    address='07804b6667d649c819dfa94af50c782c26f5abc3',
                    call_data_length=264,
                    method_id='f153cc32',
                    encoded_call_data=(
                        '730534100000000000000000000000000'
                        '00000000000000000000000000000000000'
                        '00020000000000000000000000000000000'
                        '00000000000000000000000000000000000'
                        '00000000000000000000000000000000000'
                        '00000000000000000000000000000000000'
                        '0000000000000000fd5952ef8de4707f95e'
                        '754299e8c0ffd1e876f3400000000000000'
                        '00000000000000000000000000000000000'
                        '0000000000000a000000000000000000000'
                        '00000000000000000000000000000000000'
                        '000000033697066733a516d596277436637'
                        '4d6e6932797a31553358334769485667396'
                        'f35316a6b53586731533877433257547755'
                        '68485900000000000000000000000000'
                    )
                )
            ]
        )
    )
)


@pytest.fixture(scope='module', params=positive_examples)
def positive_example(request):
    """Get positive test case for parsing."""
    return request.param.raw_script, request.param.parsed_script


def test_positive_examples(positive_example):
    """Run tests for positive parsing examples."""
    script_code, prepared = positive_example
    parsed = parse_script(script_code)

    assert parsed.spec_id == prepared.spec_id
    assert len(prepared.calls) == len(parsed.calls)

    for prepared_call, parsed_call in zip(
            prepared.calls, parsed.calls
    ):
        assert parsed_call.address == prepared_call.address
        assert parsed_call.call_data_length == prepared_call.call_data_length
        assert parsed_call.method_id == prepared_call.method_id
        assert parsed_call.encoded_call_data == prepared_call.encoded_call_data


negative_examples = (
    # Invalid numbers of data bytes;
    # incorrect counter wrt to origin.
    ParsingTestCase(
        raw_script='0x000000017899ef901ed9b331baf7759'
                   'c15d2e8728e8c2a2c00000043ae962acf'
                   '000000000000000000000000000000000'
                   '000000000000000000000000000000100'
                   '000000000000000000000000000000000'
                   '000000000000000000000000000c9',
        parsed_script=None
    ),
    # Invalid numbers of data bytes;
    # more bytes wrt to origin.
    ParsingTestCase(
        raw_script='0x000000017899ef901ed9b331baf7759'
                   'c15d2e8728e8c2a2c00000044ae962acf'
                   '000000000000000000000000000000000'
                   '000000000000000000000000000000100'
                   '000000000000000000000000000000000'
                   '0000000000000000000000000000000c9',
        parsed_script=None
    ),
    # Invalid numbers of data bytes;
    # less bytes wrt to origin.
    ParsingTestCase(
        raw_script='0x000000017899ef901ed9b331baf7759'
                   'c15d2e8728e8c2a2c00000044ae962acf'
                   '000000000000000000000000000000000'
                   '000000000000000000000000000000100'
                   '000000000000000000000000000000000'
                   '0000000c9',
        parsed_script=None
    ),
    # Incorrect address length.
    ParsingTestCase(
        raw_script='0x0000000104b6667d649c819dfa94a'
                   'f50c782c26f5abc300000024945233e200'
                   '0000000000000000000000922c10dafffb'
                   '8b9be4c40d3829c8c708a12827f3',
        parsed_script=None
    )
)


@pytest.fixture(scope='module', params=negative_examples)
def negative_example(request):
    """Get negative test case for parsing."""
    return request.param.raw_script


def test_negative_examples(negative_example):
    """Run tests for negative parsing examples."""
    broken_script_code = negative_example[0]

    with pytest.raises(ParseMismatchLength):
        _ = parse_script(broken_script_code)
