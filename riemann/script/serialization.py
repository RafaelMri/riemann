import riemann
from .opcodes import CODE_TO_INT, INT_TO_CODE


def serialize(script_string):
    '''
    str -> bytearray
    '''
    string_tokens = script_string.split()
    serialized_script = bytearray()

    for token in string_tokens:
        if token == 'OP_CODESEPARATOR':
            raise NotImplementedError('OP_CODESEPARATOR is a bad idea.')
        try:
            serialized_script.extend(
                [riemann.network.CODE_TO_INT_OVERWRITE[token]])
            continue  # Skip rest of loop
        except (AttributeError, KeyError):
            pass
        try:
            serialized_script.extend([CODE_TO_INT[token]])  # Put it in there
            continue  # Skip rest of loop
        except KeyError:
            pass

        token_bytes = bytes.fromhex(token)

        if len(token_bytes) > 75:
            # TODO
            raise NotImplementedError('OP_PUSHDATA1-4 not supported yet.')

        op = 'OP_PUSH_{}'.format(len(token_bytes))
        serialized_script.extend([CODE_TO_INT[op]])
        serialized_script.extend(token_bytes)

    return serialized_script


def hex_serialize(script_string):
    '''
    str -> hex_str
    '''
    return serialize(script_string).hex()


def deserialize(serialized_script):
    '''
    bytearray -> str
    '''
    deserialized = []
    i = 0
    while i < len(serialized_script):
        current_byte = serialized_script[i]
        if current_byte == 0xab:
            raise NotImplementedError('OP_CODESEPARATOR is a bad idea.')
        if current_byte <= 75 and current_byte != 0:

            deserialized.append(
                serialized_script[i + 1: i + 1 + current_byte].hex())

            i += 1 + current_byte
            if i > len(serialized_script):
                raise IndexError(
                    'Push {} caused out of bounds exception.'
                    .format(current_byte))

        else:
            if current_byte in riemann.network.INT_TO_CODE_OVERWRITE:
                deserialized.append(
                    riemann.network.INT_TO_CODE_OVERWRITE[current_byte])
            elif current_byte in INT_TO_CODE:
                deserialized.append(INT_TO_CODE[current_byte])
            else:
                raise ValueError(
                    'Unsupported opcode. '
                    'Got 0x%x' % serialized_script[i])
            i += 1

    return ' '.join(deserialized)


def hex_deserialize(script_hex):
    '''
    bytearray -> hex_str
    '''
    return deserialize(bytes.fromhex(script_hex))
