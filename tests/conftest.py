"""Settings for tests."""
import pytest


def pytest_addoption(parser):
    """Add CLI parameters for tests."""
    parser.addoption(
        '--apikey', type=str,
        default=None, help='API key for Etherscan.'
    )


@pytest.fixture(scope='session')
def api_key(pytestconfig) -> str:
    """Return apikey from CLI parameters."""
    return pytestconfig.getoption('apikey')
