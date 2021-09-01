"""
Combined ABI provider, APIEtherscan with local directory.
"""
import logging

from typing import Optional

from .base import ABI_T
from .etherscan import ABIProviderEtherscanApi
from .local import ABIProviderLocalOneFile

from evmscript_parser.core.exceptions import (
    ABIEtherscanNetworkError, ABIEtherscanStatusCode
)


class ABIProviderCombined(
    ABIProviderLocalOneFile, ABIProviderEtherscanApi
):
    """
    Combined way of getting ABI
    """

    def __init__(
            self,
            api_key: str, target_interface: str,
            specific_net: Optional[str] = None,
            retries: int = 5, proxy_punching: bool = True
    ):
        """Initialize Etherscan API and local providers."""
        ABIProviderEtherscanApi.__init__(
            self, api_key, specific_net, retries, proxy_punching
        )
        ABIProviderLocalOneFile.__init__(
            self, target_interface
        )

    def get_abi(self, address: str, *args, **kwargs) -> ABI_T:
        """Return ABI."""
        try:
            return ABIProviderEtherscanApi.get_abi(
                self, address, *args, **kwargs
            )
        except (ABIEtherscanNetworkError, ABIEtherscanStatusCode) as err:
            logging.exception(
                f'ABIProviderCombined: '
                f'Getting ABI through Etherscan API failed: '
                f'{repr(err)}')

        return ABIProviderLocalOneFile.get_abi(
            *args, **kwargs
        )
