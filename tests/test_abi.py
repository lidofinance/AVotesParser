"""Tests of getting ABI from different sources."""
from evmscript_parser.core.decode import decode_function_call
from evmscript_parser.core.decode.ABI import ABIProviderEtherscanApi


def test_etherscan_api(api_key, abi_positive_example):
    """Run tests for getting ABI from Etherscan API."""
    contract, sign, name = abi_positive_example
    abi_provider = ABIProviderEtherscanApi(
        api_key, 'mainnet', retries=3
    )
    assert decode_function_call(
        contract, sign,
        '', abi_provider
    ).function_name == name
