"""
Getting contracts ABI through Etherscan API.
"""
import json
import time
import logging
import requests

import brownie

from functools import lru_cache, partial
from typing import Optional, Dict, Tuple

from evmscript_parser.core.exceptions import (
    ABIEtherscanNetworkError, ABIEtherscanStatusCode
)

from .base import (
    ABIProvider, ABI_T
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
# ================================ Utilities =================================
# ============================================================================


@lru_cache(maxsize=CACHE_SIZE)
def _send_query(
        module: str, action: str, api_key: str, address: str,
        retries: int, specific_net: str
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
    :exception ABIEtherscanNetworkError in case of error at network layer.
    :exception ABIEtherscanStatusCode in case of error in api calls.
    """
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
    for ind in range(retries):
        logging.debug(
            f'Send query to Etherscan API; retry: {ind + 1}/{retries}; '
            f'sleep for {initial_wait} seconds.'
        )
        time.sleep(initial_wait)

        response = requests.get(query, headers={'User-Agent': ''})
        try:
            response.raise_for_status()
        except requests.HTTPError as err:
            raise ABIEtherscanNetworkError(repr(err))

        data = response.json()

        if data['status'] == SUCCESS:
            return data['result']

        initial_wait += increase_wait
        increase_wait *= 2

    raise ABIEtherscanStatusCode(
        status_code=str(data.get('status', -1)),
        message=data.get('message', 'unknown'),
        result=data.get('result', '')
    )


"""Alias for calling getabi functionality."""
_get_contract_abi = partial(_send_query, 'contract', 'getabi')


def get_abi(
        api_key: str, address: str, specific_net: str,
        retries: int = 5
) -> ABI_T:
    """
    Get ABI of target contract by calling to Etherscan API.

    :param api_key: str, API credentials.
    :param address: str, address of target contract.
    :param retries: int, number of retry in case of unsuccessful api call.
    :param specific_net: str, name of target net.
    :return: List[Dict[str, Any]], abi description.
    :exception HTTPError in case of error at network layer.
    :exception RuntimeError in case of error in api calls.
    """
    return json.loads(_get_contract_abi(
        api_key, address, retries, specific_net
    ))


@lru_cache(maxsize=CACHE_SIZE)
def _punched_proxy() -> Dict[Tuple[str, str], str]:
    return dict()


def get_implementation_address(
        proxy_address: str, proxy_abi: ABI_T, specific_net: str
) -> str:
    """Get address from behind proxy."""
    storage = _punched_proxy()
    key = (proxy_address, specific_net)

    if key not in storage:
        if not brownie.network.is_connected():
            # WEB3_INFURA_PROJECT_ID should be set in environment.
            logging.debug(
                f'Connect to {specific_net}.'
            )
            brownie.network.connect(specific_net)

        logging.debug(
            f'Get address of implementation from {proxy_address} '
            f'in {specific_net}.'
        )
        storage[key] = brownie.Contract.from_abi(
            f'ProxyAt{proxy_address}', proxy_address, proxy_abi
        ).implementation()

    return storage[key]


# ============================================================================
# ============================== ABI =========================================
# ============================================================================


class ABIProviderEtherscanApi(ABIProvider):
    """
    Provide ABI description by using Etherscan API.
    """

    def __init__(
            self, api_key: str,
            specific_net: Optional[str] = None,
            retries: int = 5,
            proxy_punching: bool = True
    ):
        """
        Prepare API caller instance.

        :param api_key: str, Etherscan API key.
        :param specific_net: str, target net.
        :param retries: int, number of retry tries to call API.
        :param proxy_punching: bool, try to get implementation
         behind a proxy.
        """
        if specific_net is None:
            specific_net = DEFAULT_NET

        self._api_key = api_key
        self._specific_net = specific_net
        self._retries = retries
        self._through_proxy = proxy_punching

    def get_abi(self, address: str, *args, **kwargs) -> ABI_T:
        """
        Get ABI from Etherscan API.

        :param address:
        :param args: None
        :param kwargs: None
        :return: List[Dict[str, Any]], ABI description.
        :exception HTTPError in case of error at network layer.
        :exception RuntimeError in case of error in api calls.
        """
        abi = get_abi(
            self._api_key, address, self._specific_net, self._retries
        )
        if not self._through_proxy:
            return abi

        names = {
            entry.get('name', 'unknown'): entry
            for entry in abi
        }

        if 'proxyType' not in names or 'implementation' not in names:
            return abi

        logging.debug(
            f'Proxy punching for {address} '
            f'in {self._specific_net}.'
        )
        address = get_implementation_address(
            address, abi, self._specific_net
        )

        return get_abi(
            self._api_key, address, self._specific_net, self._retries
        )
