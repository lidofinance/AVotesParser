"""Settings for tests."""
import os

import brownie.network
import pytest


def pytest_addoption(parser):
    """Add CLI parameters for tests."""
    parser.addoption(
        '--apikey', type=str,
        default=None, help='API key for Etherscan.'
    )
    parser.addoption(
        '--infura-id', type=str,
        default=None, help='Infura project ID '
                           'for interaction with goerli.'
    )


@pytest.fixture(scope='session')
def api_key(pytestconfig) -> str:
    """Return apikey from CLI parameters."""
    return pytestconfig.getoption('apikey')


@pytest.fixture(scope='session')
def infura_prt_id(pytestconfig) -> str:
    """Return WEB3_INFURA_PROJECT_ID."""
    return pytestconfig.getoption('infura_id')


@pytest.fixture(scope='session')
def target_net() -> str:
    """Get target net."""
    return 'goerli'


@pytest.fixture(scope='session', autouse=True)
def prepare_brownie_network(infura_prt_id):
    """Set INFURA environment variable and disconnect from dev net."""
    os.environ['WEB3_INFURA_PROJECT_ID'] = infura_prt_id
    if brownie.network.is_connected():
        brownie.network.disconnect()
