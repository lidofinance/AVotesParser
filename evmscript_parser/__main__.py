"""
CLI of EVM scripts parser.
"""
import argparse

from mimetypes import guess_type, types_map

from .core.parse import parse
from .package import CLI_NAME
from .abi.etherscan import (
    get_abi, DEFAULT_NET, NET_URL_MAP
)


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        add_help=True,
        description=__doc__,
        prog=CLI_NAME
    )

    parser.add_argument('evmscript',
                        type=str,
                        help='Encoded script string.')
    parser.add_argument('apitoken',
                        type=str,
                        help='API key as string or a path to txt file '
                             'with it.')

    parser.add_argument('--output-json',
                        type=str,
                        default=None,
                        help='Store to json.')
    parser.add_argument('--net',
                        type=str,
                        default=DEFAULT_NET,
                        help=f'net name is case-insensitive, '
                             f'default is {DEFAULT_NET}',
                        choices=NET_URL_MAP.keys())

    return parser.parse_args()


def main():
    """Describe utils functionality."""
    args = parse_args()

    m_type, _ = guess_type(args.apitoken)
    if m_type == types_map['.txt']:
        with open(args.apitoken, 'r') as api_token_file:
            token = api_token_file.read().strip()

    else:
        token = args.apitoken

    parsed = parse(args.evmscript)
    for call in parsed.calls:
        call.abi = get_abi(token, call.address, args.net)

    print(f'Parsed:\n{repr(parsed)}')

    if args.output_json:
        with open(args.output_json, 'w') as output_file:
            output_file.write(parsed.to_json())


if __name__ == '__main__':
    main()
