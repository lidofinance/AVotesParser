"""
Provider for getting ABI from local .json files.
"""
import os
import glob
import json

from functools import lru_cache

from .base import ABIProvider, ABI_T

from evmscript_parser.core.exceptions import (
    ABILocalFileNotExisted
)


@lru_cache(maxsize=128)
def _read_interfaces(directory: str) -> ABI_T:
    """Read all json files from directory."""

    def __read_json(file: str) -> ABI_T:
        with open(file, 'r') as f:
            return json.load(f)

    return sum(
        [
            __read_json(interface)
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


class ABIProviderLocalOneFile(ABIProvider):
    """
    Store ABI specification get from target file.
    """

    def __init__(self, target_file: str):
        """Read ABI from target file."""
        if not os.path.isfile(target_file):
            raise ABILocalFileNotExisted(target_file)
        with open(target_file, 'r') as f:
            self._abi = json.load(f)

    def get_abi(self, *args, **kwargs) -> ABI_T:
        """Return ABI."""
        return self._abi
