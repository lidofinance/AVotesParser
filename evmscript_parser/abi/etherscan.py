"""
Getting contracts ABI through Etherscan API.
"""
import json
import time
import requests

from functools import lru_cache, partial
from typing import (
    Optional, Dict, Any
)

# ============================================================================
# ===================== Constants ============================================
# ============================================================================

DEFAULT_NET = 'goerli'
NET_URL_MAP = {
    'mainnet': 'https://api.etherscan.io',
    'goerli': 'https://api-goerli.etherscan.io',
    'kovan': 'https://api-kovan.etherscan.io',
    'rinkebay': 'https://api-rinkeby.etherscan.io',
    'ropsten': 'https://api-ropsten.etherscan.io'
}
SUCCESS = '1'
MINIMUM_RETRIES = 1
CACHE_SIZE = 128


# ============================================================================
# ================================ API Caller ================================
# ============================================================================


@lru_cache(maxsize=CACHE_SIZE)
def _send_query(
        module: str, action: str, api_key: str, address: str,
        retries: int = MINIMUM_RETRIES, specific_net: Optional[str] = None
) -> str:
    """
    Send query to Etherscan API.

    :param module: str, part of Etherscan API.
    :param action: str, concrete function from API.
    :param api_key: str, API credentials.
    :param address: str, address of target contract.
    :param retries: int, number of retry in case of unsuccessful api call.
    :param specific_net: str, name of target net.
    :return: str, encoded json description of abi.
    :exception HTTPError in case of error at network layer.
    :exception RuntimeError in case of error in api calls.
    """
    if specific_net is None:
        specific_net = DEFAULT_NET

    retries = max(MINIMUM_RETRIES, retries)

    if specific_net not in NET_URL_MAP:
        raise KeyError(f'Unexpected name of net. '
                       f'Should be one of: '
                       f'{str(NET_URL_MAP.keys())}')

    url = NET_URL_MAP[specific_net]
    parameters = '&'.join([
        f'{name}={value}'
        for name, value in zip(
            ['module', 'action', 'address', 'apikey'],
            [module, action, address, api_key]
        )
    ])
    query = f'{url}/api?{parameters}'

    data = {}
    initial_wait = 0
    increase_wait = 1
    for _ in range(retries):
        time.sleep(initial_wait)

        response = requests.get(query, headers={'User-Agent': ''})
        response.raise_for_status()

        data = response.json()

        if data['status'] == SUCCESS:
            return data['result']

        initial_wait += increase_wait
        initial_wait *= 2

    failed_reason = data.get('message', 'unknown')
    raise RuntimeError(f'Failed reason: {failed_reason}')


"""Alias for calling getabi functionality."""
_get_contract_abi = partial(_send_query, 'contract', 'getabi')


def get_abi(
        api_key: str, address: str, specific_net: str,
        retries: int = 6
) -> Dict[str, Any]:
    """
    Get ABI of target contract by calling to Etherscan API.

    :param api_key: str, API credentials.
    :param address: str, address of target contract.
    :param retries: int, number of retry in case of unsuccessful api call.
    :param specific_net: str, name of target net.
    :return: Dict[str, Any], abi description.
    :exception HTTPError in case of error at network layer.
    :exception RuntimeError in case of error in api calls.
    """
    return json.loads(_get_contract_abi(
        api_key, address, retries, specific_net
    ))
