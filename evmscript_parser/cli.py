"""
Observation for the last N running votes at the aragon voting.
"""
import argparse
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache, partial
from mimetypes import guess_type, types_map
from typing import Union, List

import brownie

from .core.ABI import get_cached_etherscan_api
from .core.ABI.storage import CachedStorage
from .core.ABI.utilities.etherscan import (
    DEFAULT_NET, NET_URL_MAP,
    get_abi, get_implementation_address
)
from .core.decode.structure import Call
from .core.decoding import decode_evm_script, calls_info_pretty_print
from .package import CLI_NAME

DEFAULT_ARAGON_ADDRESS = '0x2e59A20f205bB85a89C53f1936454680651E618e'


def read_key(path_to: str) -> str:
    """Read Etherscan API key."""
    m_type, _ = guess_type(path_to)
    if m_type == types_map['.txt']:
        with open(path_to, 'r') as api_token_file:
            return api_token_file.read().strip()

    else:
        return path_to


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        add_help=True,
        description=__doc__,
        prog=CLI_NAME
    )

    parser.add_argument('apitoken',
                        type=str,
                        help='Etherscan API key as string or '
                             'a path to txt file with it.')

    parser.add_argument('-n',
                        type=int,
                        default=10,
                        help='Parse last N votes.')
    parser.add_argument('--net',
                        type=str,
                        default=DEFAULT_NET,
                        help=f'net name is case-insensitive, '
                             f'default is {DEFAULT_NET}',
                        choices=NET_URL_MAP.keys())
    parser.add_argument('--aragon-voting-address',
                        type=str,
                        default=DEFAULT_ARAGON_ADDRESS,
                        help='Address of aragon voting contract')
    parser.add_argument('--debug',
                        action='store_true',
                        help='Show debug messages')
    parser.add_argument('--retries',
                        type=int,
                        default=5,
                        help='Number of retries of calling Etherscan API.')

    return parser.parse_args()


def logging_settings(debug: bool) -> None:
    """Prepare logger."""
    if debug:
        level = logging.DEBUG

    else:
        level = logging.INFO

    logging.basicConfig(
        format='%(levelname)s:%(message)s', level=level
    )


@lru_cache
def get_aragon_voting(
        net: str, address: str,
        etherscan_api_key: str, retries: int,
):
    """Get aragon voting contract as object."""
    if not brownie.network.is_connected():
        brownie.network.connect(net)

    abi = get_abi(etherscan_api_key, address, net, retries)
    impl_address = get_implementation_address(
        address, abi, net
    )
    impl_abi = get_abi(etherscan_api_key, impl_address, net, retries)
    return brownie.Contract.from_abi(
        'AragonVoting', address, impl_abi
    )


def parse_voting(
        aragon_voting, abi_storage: CachedStorage,
        vote_number: int
) -> List[Union[Call, str]]:
    """Decode aragon voting with specific number."""
    script_code = str(aragon_voting.getVote(vote_number)[-1])
    return decode_evm_script(script_code, abi_storage)


def main():
    """Contain main script."""
    args = parse_args()

    logging_settings(args.debug)
    token = read_key(args.apitoken)

    logging.debug(f'API key: {token}')

    aragon_voting = get_aragon_voting(
        args.net, args.aragon_voting_address,
        token, args.retries
    )

    last_vote_number = aragon_voting.votesLength()

    abi_storage = get_cached_etherscan_api(
        token, args.net
    )

    _parse_voting = partial(parse_voting, aragon_voting, abi_storage)
    number_offset = last_vote_number - args.n
    with ThreadPoolExecutor(10) as executor:
        parsed_votes = {
            executor.submit(
                _parse_voting,
                vote_number + number_offset
            ): vote_number
            for vote_number in range(
                0, args.n
            )
        }
        results = [None] * len(parsed_votes)
        for future in as_completed(parsed_votes):
            number = parsed_votes[future]
            results[number] = future.result()

    for num, parsed_vote in enumerate(results):
        number = num + number_offset
        total = len(parsed_vote)
        print(f'Voting number {number}.')
        for ind, call in enumerate(parsed_vote):
            print(f'Point {ind + 1}/{total}')
            print(calls_info_pretty_print(call))
        print('-----------------------------------------------------\n\n')


if __name__ == '__main__':
    main()
