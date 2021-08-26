"""
Base class for ABI hierarchy.
"""
from typing import (
    List, Dict, Any
)
from abc import ABC, abstractmethod

# ============================================================================
# ======================== Types aliases =====================================
# ============================================================================

ABI_T = List[Dict[str, Any]]
METHOD_ABI_MAPPING_T = Dict[str, Dict[str, Any]]


# ============================================================================
# ============================== ABI =========================================
# ============================================================================


class ABIProvider(ABC):
    """
    Base class for ABI providers.
    """

    @abstractmethod
    def get_abi(self, *args, **kwargs) -> ABI_T:
        """Return ABI."""
        pass
