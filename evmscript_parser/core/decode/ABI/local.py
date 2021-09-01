"""
Provider for getting ABI from local .json files.
"""
import os
import glob
import json

from functools import lru_cache

from .base import ABIProvider, ABI_T


@lru_cache(maxsize=128)
def _read_interfaces(directory: str) -> ABI_T:
    """Read all json files from directory."""
    return sum(
        [
            json.load(interface)
            for interface
            in glob.glob(os.path.join(directory, '*.json'))
        ],
        []
    )


class ABIProviderLocal(ABIProvider):
    """
    Store ABI specification get from local directory.
    """

    def __init__(self, interface_directory: str):
        """Get cached or read ABI from directory."""
        self._abi = _read_interfaces(interface_directory)

    def get_abi(self, *args, **kwargs) -> ABI_T:
        """Return ABI"""
        return self._abi
