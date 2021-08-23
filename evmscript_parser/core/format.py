from dataclasses import dataclass, field
from typing import (
    List
)

SPEC_ID_LENGTH = 8
ADDRESS_LENGTH = 40
METHOD_ID_LENGTH = 8
CALL_DATA_LENGTH = 8

DEFAULT_SPEC_ID = '1'.zfill(SPEC_ID_LENGTH)
HEX_PREFIX = '0x'


class FormatError(TypeError):
    """Check format"""
    pass


class MismatchLength(FormatError):
    def __init__(self, field_name: str, received: int, expected: int):
        message = f'Length of {field_name} should be: {expected}; ' \
                  f'received: {received}.'
        super().__init__(message)


def _with_hex_prefix(data: str) -> str:
    return f'{HEX_PREFIX}{data}'


@dataclass
class OneCall:
    # 20 bytes
    address: str
    # 4 bytes
    call_data_length: int
    # 4 bytes
    method_id: str
    # call_data_length - 4 bytes
    encoded_call_data: str

    def __post_init__(self):
        if len(self.address) != ADDRESS_LENGTH:
            raise MismatchLength(
                'address', len(self.address), ADDRESS_LENGTH
            )

        if len(self.method_id) != METHOD_ID_LENGTH:
            raise MismatchLength(
                'method id', len(self.method_id), METHOD_ID_LENGTH
            )

        call_data_length_without_method_id = (
                self.call_data_length * 2 - len(self.method_id)
        )
        if len(self.encoded_call_data) != call_data_length_without_method_id:
            raise MismatchLength(
                'encoded call data',
                len(self.encoded_call_data),
                call_data_length_without_method_id
            )

        self.address = _with_hex_prefix(self.address)
        self.method_id = _with_hex_prefix(self.method_id)
        self.encoded_call_data = _with_hex_prefix(self.encoded_call_data)


@dataclass
class EVMScript:
    # Script executor id
    spec_id: str = field(default=DEFAULT_SPEC_ID)
    # Calls data
    calls: List[OneCall] = field(default_factory=list)

    def __post_init__(self):
        if len(self.spec_id) != SPEC_ID_LENGTH:
            raise MismatchLength(
                'spec id', len(self.spec_id), SPEC_ID_LENGTH
            )

        self.spec_id = _with_hex_prefix(self.spec_id)
