"""
Description of function calling as structure.
"""
from dataclasses import dataclass
from typing import List, Any, Dict, Optional


@dataclass
class FuncInput:
    """
    Single function input
    """

    name: str
    type: str
    value: Any

    def __post_init__(self):
        """Conversion from raw bytes to string for bytes values."""
        if callable(getattr(self.value, 'hex', None)):
            self.value = self.value.hex()


@dataclass
class Call:
    """
    Single function call
    """

    contract_address: str
    function_signature: str
    function_name: str
    inputs: List[FuncInput]
    properties: Dict[str, Any]
    outputs: Optional[List[Any]]
