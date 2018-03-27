import io
import boto3
import pytest

from moto import mock_ec2
from unittest.mock import patch
from argparse import Namespace
from awswl import commands
import os

AWS_DEFAULT_REGION = 'AWS_DEFAULT_REGION'


@pytest.fixture(name='region', scope='function')
def region_fixture():
    region = 'ca-central-1'
    os.environ[AWS_DEFAULT_REGION] = region
    yield region
    del os.environ[AWS_DEFAULT_REGION]


@pytest.fixture(name='security_group', scope='function')
def security_group_fixture():
    mock_ec2().start()
    ec2 = boto3.resource('ec2')
    sg = ec2.create_security_group(
        Description='Security Group for SSH Whitelisting',
        GroupName='SSH Whitelist',
        VpcId='vpc-123'
    )
    yield sg
    mock_ec2().stop()


@patch('sys.stdout', new_callable=io.StringIO)
def test_version_command(mock_stdout):
    # Given
    opt = Namespace()
    opt.version = "1.2.3"

    # When
    commands.cmd_version(opt)

    # Then
    assert mock_stdout.getvalue() == "awswl v1.2.3\n"


# noinspection PyUnusedLocal
def test_list_command_lists_no_blocks(region, security_group):
    assert_list_output(options(security_group), "No CIDR blocks authorized for SSH")


def test_list_command_lists_ipv4_blocks(region, security_group):
    security_group.authorize_ingress(IpPermissions=[{
        'IpRanges': [
            {'CidrIp': '10.0.0.1/32'},
            {'CidrIp': '10.0.1.0/24'}
        ],
        'IpProtocol': 'tcp',
        'FromPort': 22,
        'ToPort': 22
    }])
    assert_list_output(options(security_group), ["- 10.0.0.1/32\n", "- 10.0.1.0/24\n"])


def test_list_command_identifies_enclosing_blocks(region, security_group):
    security_group.authorize_ingress(IpPermissions=[{
        'IpRanges': [
            {'CidrIp': '192.0.2.1/32'},
            {'CidrIp': '192.0.2.0/24'},
            {'CidrIp': '192.0.1.0/24'}
        ],
        'IpProtocol': 'tcp',
        'FromPort': 22,
        'ToPort': 22
    }])
    assert_list_output(
        options(security_group),
        ["- 192.0.2.1/32 (current)\n", "- 192.0.2.0/24 (current)\n", "- 192.0.1.0/24\n"]
    )


@mock_ec2
def test_list_command_without_region_shows_error():
    assert 'AWS_DEFAULT_REGION' not in os.environ
    opt = Namespace()
    opt.sgid = 'sg-12345'
    assert_list_output(opt, "No AWS region specified")


def options(security_group):
    opt = Namespace()
    opt.sgid = security_group.id
    opt.ssh_port = 22
    return opt


@patch('awswl.externalip.get_external_ip', return_value='192.0.2.1')
@patch('sys.stdout', new_callable=io.StringIO)
def assert_list_output(opt, matches, mock_stdout, exip_method):
    commands.cmd_list(opt)
    output = mock_stdout.getvalue()
    if isinstance(matches, str):
        assert matches in output
    if isinstance(matches, list):
        for match in matches:
            assert match in output


@patch('awswl.externalip.get_external_ip', return_value='192.0.2.1')
@patch('sys.stdout', new_callable=io.StringIO)
def test_remove_current_removes_permission(mock_stdout, exip_method, region, security_group):
    security_group.authorize_ingress(IpPermissions=[{
        'IpRanges': [
            {'CidrIp': '192.0.2.1/32'},
        ],
        'IpProtocol': 'tcp',
        'FromPort': 22,
        'ToPort': 22
    }])
    opt = options(security_group)
    commands.cmd_remove_current(opt)

    after_group = boto3.resource('ec2').SecurityGroup(security_group.id)
    assert not after_group.ip_permissions
    assert "Removed current ip address" in mock_stdout.getvalue()

@patch('awswl.externalip.get_external_ip', return_value='192.0.2.1')
@patch('sys.stdout', new_callable=io.StringIO)
def test_remove_current_removes_permission_notfound(mock_stdout, exip_method, region, security_group):
    opt = options(security_group)
    commands.cmd_remove_current(opt)
    assert "Current IP address does not seem to be whitelisted." in mock_stdout.getvalue()
