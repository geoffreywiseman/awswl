import os
import pytest

from awswl import cli


@pytest.fixture
def envsgid():
    sgid = "sg-12345"
    os.environ[cli.AWSWL_SGID_KEY] = sgid
    yield sgid
    os.environ.unsetenv(cli.AWSWL_SGID_KEY)


def test_parse_empty_arguments():
    options = cli.parse_args([])
    assert options.ssh_port == 22
    assert options.sgid is None


# noinspection PyShadowingNames
def test_parse_environment_into_arguments(envsgid):
    options = cli.parse_args([])
    assert options.sgid == envsgid


# noinspection PyShadowingNames
def test_parse_override_defaults(envsgid):
    override = 'sg-67890'
    options = cli.parse_args(['--sgid', override])
    assert options.sgid == override
    assert options.sgid != envsgid
