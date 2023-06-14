import io
import boto3
import pytest

from moto import mock_ec2
from argparse import Namespace
from awswl import commands
import os

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

AWS_DEFAULT_REGION = 'AWS_DEFAULT_REGION'


@pytest.fixture(name='region', scope='function')
def region_fixture():
    region = 'ca-central-1'
    os.environ[AWS_DEFAULT_REGION] = region
    yield region
    if AWS_DEFAULT_REGION in os.environ:
        del os.environ[AWS_DEFAULT_REGION]


@pytest.fixture(name='security_group', scope='function')
def security_group_fixture():
    mock = mock_ec2()
    mock.start()
    ec2 = boto3.resource('ec2')
    sg = ec2.create_security_group(
        Description='Security Group for SSH allowlisting',
        GroupName='SSH allowlist',
        VpcId='vpc-123'
    )
    yield sg
    mock.stop()


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


# TODO: Not currently triggered by moto -- need to research how to trigger again.
# @mock_ec2
# def test_list_command_without_region_shows_error():
#     assert 'AWS_DEFAULT_REGION' not in os.environ
#     assert 'AWS_REGION' not in os.environ
#     opt = Namespace()
#     opt.sgid = 'sg-12345'
#     assert_list_output(opt, "No AWS region specified")


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
def test_add_current_adds_permission(mock_stdout, exip_method, region, security_group):
    assert not security_group.ip_permissions
    opt = options(security_group)
    commands.cmd_add_current(opt)

    after_group = boto3.resource('ec2').SecurityGroup(security_group.id)
    assert len(after_group.ip_permissions) == 1
    ranges = after_group.ip_permissions[0]['IpRanges']
    assert len(ranges) == 1
    assert ranges[0]['CidrIp'] == '192.0.2.1/32'
    assert "Added current external IP address as a CIDR block" in mock_stdout.getvalue()


@patch('sys.stdout', new_callable=io.StringIO)
def test_add_adds_specified_permission(mock_stdout, region, security_group):
    assert not security_group.ip_permissions
    opt = options(security_group)
    commands.cmd_add(opt, '192.0.2.1/24')

    after_group = boto3.resource('ec2').SecurityGroup(security_group.id)
    assert len(after_group.ip_permissions) == 1
    ranges = after_group.ip_permissions[0]['IpRanges']
    assert len(ranges) == 1
    assert ranges[0]['CidrIp'] == '192.0.2.0/24'
    assert "Added specified CIDR block" in mock_stdout.getvalue()


@patch('awswl.externalip.get_external_ip', return_value='192.0.2.1')
@patch('sys.stdout', new_callable=io.StringIO)
def test_remove_current_removes_permission(mock_stdout, exip_method, region,
                                           security_group):
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
    assert "Removed current external IP address as a CIDR block" \
           in mock_stdout.getvalue()


@patch('awswl.externalip.get_external_ip', return_value='192.0.2.1')
@patch('sys.stdout', new_callable=io.StringIO)
def test_remove_current_indicates_notfound(mock_stdout, exip_method, region,
                                           security_group):
    opt = options(security_group)
    commands.cmd_remove_current(opt)
    assert \
        "Current external IP address as a CIDR block does not seem to be allowlisted." \
        in mock_stdout.getvalue()


@patch('sys.stdout', new_callable=io.StringIO)
def test_remove_removes_specified(mock_stdout, region, security_group):
    security_group.authorize_ingress(IpPermissions=[{
        'IpRanges': [
            {'CidrIp': '192.0.2.1/32'},
        ],
        'IpProtocol': 'tcp',
        'FromPort': 22,
        'ToPort': 22
    }])
    opt = options(security_group)
    commands.cmd_remove(opt, '192.0.2.1/32')

    after_group = boto3.resource('ec2').SecurityGroup(security_group.id)
    assert not after_group.ip_permissions
    assert "Removed specified CIDR block" in mock_stdout.getvalue()


@patch('sys.stdout', new_callable=io.StringIO)
def test_remove_specified_indicates_notfound(mock_stdout, region, security_group):
    opt = options(security_group)
    commands.cmd_remove(opt, '192.0.2.1/32')
    assert "Specified CIDR block does not seem to be allowlisted." \
           in mock_stdout.getvalue()
