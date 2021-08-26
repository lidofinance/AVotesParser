"""
Decoding functions callings to human-readable format.
"""
import web3

from typing import Dict, List, Any

from sha3 import keccak_256

from ..script_specification import HEX_PREFIX

from .structure import Call, FuncInput
from .ABI.base import ABIProvider, ABI_T, METHOD_ABI_MAPPING_T


# ============================================================================
# ========================= Utilities ========================================
# ============================================================================

def _get_encoded_signature(func_name: str, input_types: List[str]) -> str:
    """
    Encode signature of function according to the ABI specification.

    :param func_name: str, function name
    :param input_types: List[str], list with inputs types for function.
    :return: str, first fours bytes of encoded function.

    The result of encoding is:

    keccak256('func_name(input_type1,input_type2,...)')
    """
    input_types = ','.join(input_types)
    signature = f'{func_name}({input_types})'
    keccak = keccak_256()
    keccak.update(signature.encode('ascii'))
    return f'0x{keccak.hexdigest()[:8]}'


def _gather_types(inputs: List[Dict[str, Any]]) -> List[str]:
    """
    Parse input json ABI description for function input types.

    :param inputs: List[Dict[str, Any]], 'inputs' entry of a json description.
    :return: List[str], gathered types.
    """

    def __extract_type(entity: Dict[str, Any]) -> str:
        if 'components' in entity:
            t = ','.join(_gather_types(
                entity['components']
            ))
            return f'({t})'

        return entity['type']

    return [
        __extract_type(inp)
        for inp in inputs
    ]


def with_decoded_signatures(
        contract_abi: ABI_T
) -> METHOD_ABI_MAPPING_T:
    """Create mapping from function signatures to function descriptions."""

    def __is_function(entity: Dict[str, Any]) -> bool:
        t = entity['type']
        if t == 'function' or t == 'receive':
            return True

        return False

    return {
        _get_encoded_signature(
            entry['name'],
            _gather_types(entry['inputs'])
        ): entry
        for entry
        in filter(
            __is_function, contract_abi
        )
    }


# ============================================================================
# ================================= Decoding =================================
# ============================================================================

def decode_function_call(
        contract_address: str, function_signature: str, call_data: str,
        abi_provider: ABIProvider
) -> Call:
    """
    Decode function call.

    :param contract_address: str, contract addres.
    :param function_signature: str, the first fourth bytes
                                    of function signature
    :param call_data: str, encoded call data.
    :param abi_provider: ABIProvider, instance for getting ABI.
    :return: Call, decoded description of function calling.
    """
    abi = abi_provider.get_abi(
        address=contract_address, singature=function_signature
    )

    function_description = with_decoded_signatures(
        abi
    ).get(function_signature, None)

    if function_description is None:
        return function_description

    address = web3.Web3.toChecksumAddress(contract_address)
    contract = web3.Web3().eth.contract(
        address=address, abi=abi
    )

    inputs_spec = function_description['inputs']

    if call_data.startswith(HEX_PREFIX):
        call_data = call_data[len(HEX_PREFIX):]

    _, decoded_inputs = contract.decode_function_input(
        f'{function_signature}{call_data}'
    )

    inputs = [
        FuncInput(
            inp['name'],
            inp['type'],
            decoded_inputs[inp['name']]
        )
        for inp in inputs_spec
    ]

    properties = {
        'constant': function_description.get(
            'constant', 'unknown'
        ),
        'payable': function_description.get(
            'payable', 'unknown'
        ),
        'stateMutability': function_description.get(
            'stateMutability', 'unknown'
        ),
        'type': function_description.get(
            'type', 'unknown'
        )
    }

    return Call(
        contract_address, function_signature,
        function_description.get('name', 'unknown'), inputs,
        properties, function_description['outputs']
    )
