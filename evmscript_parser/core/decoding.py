"""
High level utilities for script decoding and printing.
"""
from brownie.utils import color

from typing import Union, List

from .parse import parse_script
from .decode import decode_function_call
from .ABI.storage import CachedStorage
from .decode.structure import Call, FuncInput
from .exceptions import (
    ParseStructureError, ABIEtherscanStatusCode, ABIEtherscanNetworkError
)


def decode_evm_script(
        script: str,
        abi_storage: CachedStorage
) -> List[Union[Call, str]]:
    """
    Parse and decode EVM script.
    """
    try:
        parsed = parse_script(script)
    except ParseStructureError as err:
        return [repr(err)]

    calls = []
    for call in parsed.calls:
        try:
            call = decode_function_call(
                call.address, call.method_id,
                call.encoded_call_data, abi_storage
            )
            calls.append(call)

            for inp in call.inputs:
                if inp.type == 'bytes' and inp.name == '_evmScript':
                    inp.value = decode_evm_script(
                        inp.value.hex(),
                        abi_storage
                    )
                    break

        except (ABIEtherscanNetworkError, ABIEtherscanStatusCode) as err:
            calls.append(f'Network layer error: {repr(err)}')

    return calls


def _input_pretty_print(inp: FuncInput, tabs: int) -> str:
    offset: str = ' ' * tabs

    if isinstance(inp.value, list) and isinstance(inp.value[0], Call):
        calls = '\n'.join(
            _calls_info_pretty_print(call, tabs + 3)
            for call in inp.value
        )
        return f'{offset}{inp.name}: {inp.type} = [\n{calls}\n]'

    return f'{offset}{inp.name}: {inp.type} = {inp.value}'


def _calls_info_pretty_print(
        call: Union[str, Call], tabs: int = 0
) -> str:
    if isinstance(call, str):
        return f'Decoding failed: {call}'

    else:
        inputs = '\n'.join([
            _input_pretty_print(inp, tabs)
            for inp in call.inputs
        ])

        offset: str = ' ' * tabs

        return (
            f'{offset}Contract: {call.contract_address}\n'
            f'{offset}Function: {call.function_name}\n'
            f'{offset}Inputs:\n'
            f'{inputs}'
        )


def calls_info_pretty_print(
        call: Union[str, Call]
) -> str:
    """Format printing for Call instance."""
    return color.highlight(_calls_info_pretty_print(call))
