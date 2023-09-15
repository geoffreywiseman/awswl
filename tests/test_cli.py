import os

import pytest

from awswl import cli


@pytest.fixture(name='sgid')
def fixture_env_sgid():
    sgid = "sg-12345"
    os.environ[cli.AWSWL_SGID_KEY] = sgid
    yield sgid
    del os.environ[cli.AWSWL_SGID_KEY]


def test_parse_empty_arguments():
    options = cli.parse_args([])
    assert options.ssh_port == 22
    assert options.sgid is None
    assert options.sg_name is None


def test_parse_sgid_into_option(sgid):
    options = cli.parse_args([])
    assert options.sgid == sgid


def test_parse_override_defaults(sgid):
    override = 'sg-67890'
    options = cli.parse_args(['--sgid', override])
    assert options.sgid == override
    assert options.sgid != sgid


@pytest.fixture(name='sgname')
def fixture_env_sgname():
    sgname = "mycorp-prod-bastion"
    os.environ[cli.AWSWL_SGNAME_KEY] = sgname
    yield sgname
    del os.environ[cli.AWSWL_SGNAME_KEY]


def test_parse_sgname_env_into_option(sgname):
    options = cli.parse_args([])
    assert options.sg_name == sgname


def test_override_sgname_env(sgname):
    override = 'mycorp-beta-bastion'
    options = cli.parse_args(['--sg-name', override])
    assert options.sg_name == override
    assert options.sg_name != sgname


def test_default_desc():
    options = cli.parse_args(['--version'])
    assert options.desc is None
    assert not options.auto_desc


def test_parse_desc():
    description = 'Bastion Host'
    options = cli.parse_args(['--desc', description])
    assert options.desc == description


def test_parse_autodesc():
    options = cli.parse_args(['--auto-desc'])
    assert options.auto_desc


def test_parse_conflict():
    with pytest.raises(SystemExit):
        cli.parse_args(['--auto-desc', '--desc', 'conflict'])
