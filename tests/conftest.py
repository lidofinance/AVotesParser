"""Settings for tests."""
from typing import List
from functools import partial

from examples import Parsing


def _parametrize(
        metafunc, fixture_name: str, cases: List
) -> None:
    if fixture_name in metafunc.fixturenames:
        if hasattr(_parametrize, fixture_name):
            cases, names = getattr(
                _parametrize, fixture_name
            )

        else:
            names = [
                f'case_{ind}'
                for ind in range(len(cases))
            ]

            setattr(
                _parametrize, fixture_name, (cases, names)
            )

        metafunc.parametrize(
            fixture_name, cases, ids=names
        )


def pytest_generate_tests(metafunc):
    """Parametrize tests."""
    parametrize = partial(_parametrize, metafunc)
    for fixture_name, cases in [
        ('positive_example', Parsing.positive_examples),
        ('negative_example', Parsing.negative_examples)
    ]:
        parametrize(fixture_name, cases)
