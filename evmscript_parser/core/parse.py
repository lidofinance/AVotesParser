from .format import (
    EVMScript,
    OneCall,
    HEX_PREFIX,
    SPEC_ID_LENGTH, METHOD_ID_LENGTH, ADDRESS_LENGTH, CALL_DATA_LENGTH
)


def parse(encoded_script: str) -> EVMScript:
    if encoded_script.startswith(HEX_PREFIX):
        encoded_script = encoded_script[len(HEX_PREFIX):]
    spec_id = encoded_script[:SPEC_ID_LENGTH]

    calls_data = []
    i = SPEC_ID_LENGTH
    while i < len(encoded_script):
        address = encoded_script[i:i + ADDRESS_LENGTH]
        print(address)

        i += ADDRESS_LENGTH

        data_length = int(
            encoded_script[i:i + CALL_DATA_LENGTH], 16
        )

        i += CALL_DATA_LENGTH

        method_id = encoded_script[i:i + METHOD_ID_LENGTH]

        i += METHOD_ID_LENGTH

        offset = data_length * 2 - METHOD_ID_LENGTH

        call_data = encoded_script[i: i + offset]

        i += offset

        calls_data.append(OneCall(
            address, data_length,
            method_id, call_data
        ))

    return EVMScript(
        spec_id, calls_data
    )
