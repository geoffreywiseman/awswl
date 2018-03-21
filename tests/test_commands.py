import io
import boto3
import pytest

from moto import mock_ec2
from unittest.mock import patch
from argparse import Namespace
from awswl import commands
from pprint import pprint
import os


@pytest.fixture(name='region')
def region_fixture():
    os.environ['AWS_DEFAULT_REGION'] = 'ca-central-1'


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
    options = Namespace()
    options.version = "1.2.3"

    # When
    commands.cmd_version(options)

    # Then
    assert mock_stdout.getvalue() == "awswl v1.2.3\n"


def test_list_command_lists_no_blocks(region, security_group):
    assert_list_output(options(security_group), "No CIDR blocks authorized for SSH")


def test_list_command_lists_ipv4_blocks(region, security_group):
    security_group.authorize_ingress(IpPermissions=[{
        'IpRanges': [{'CidrIp': '10.0.0.1/32'}],
        'IpProtocol': 'tcp',
        'FromPort': 22,
        'ToPort': 22
    }])
    assert_list_output(options(security_group), "- 10.0.0.1/32\n")


def options(security_group):
    options = Namespace()
    options.sgid = security_group.id
    options.ssh_port = 22
    return options


@patch('awswl.externalip.get_external_ip', return_value='192.0.2.1')
@patch('sys.stdout', new_callable=io.StringIO)
def assert_list_output(options, substring, mock_stdout, exip_method):
    commands.cmd_list(options)
    assert substring in mock_stdout.getvalue()

# TODO: List With Blocks
# TODO: List IPV4
# TODO: List IPV6
# TODO: List Shows Current
# TODO: List NoRegion
# TODO: List ClientError
# TODO: Add Current
# TODO: Remove Current
