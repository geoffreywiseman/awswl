import os
import pytest

from awswl import cli


@pytest.fixture(name='sgid')
def fixture_env_sgid():
    sgid = "sg-12345"
    os.environ[cli.AWSWL_SGID_KEY] = sgid
    yield sgid
    os.environ.unsetenv(cli.AWSWL_SGID_KEY)


def test_parse_empty_arguments():
    options = cli.parse_args([])
    assert options.ssh_port == 22
    assert options.sgid is None


def test_parse_environment_into_arguments(sgid):
    options = cli.parse_args([])
    assert options.sgid == sgid


def test_parse_override_defaults(sgid):
    override = 'sg-67890'
    options = cli.parse_args(['--sgid', override])
    assert options.sgid == override
    assert options.sgid != sgid
