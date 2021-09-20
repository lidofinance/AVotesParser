"""Tests context."""


class ABIEtherscan:
    """Context for testing API caller."""

    positive_examples = [
        (
            'Tether.json',
            '0xdac17f958d2ee523a2206206994597c13d831ec7',
            '0x18160ddd',
            'totalSupply',
        ),
        (
            'Lido.json',
            '0xae7ab96520de3a18e5e111b5eaab095312d7fe84',
            '0x18160ddd',
            'totalSupply'
        )
    ]
