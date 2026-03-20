import os
from argparse import Namespace

import boto3
import pytest
from moto import mock_aws

_AWS_DEFAULT_REGION = 'AWS_DEFAULT_REGION'


@pytest.fixture(name='region')
def region_fixture():
    region = 'ca-central-1'
    os.environ[_AWS_DEFAULT_REGION] = region
    yield region
    if _AWS_DEFAULT_REGION in os.environ:
        del os.environ[_AWS_DEFAULT_REGION]


@pytest.fixture(name='security_group')
def security_group_fixture(region):
    with mock_aws():
        ec2 = boto3.resource('ec2', region_name=region)
        sg = ec2.create_security_group(
            Description='Security Group for SSH allowlisting',
            GroupName='SSH allowlist',
            VpcId='vpc-123'
        )
        yield sg


@pytest.fixture(name='bare_options')
def bare_options_fixture():
    """Return a Namespace pre-populated with the CLI's default option values."""
    return Namespace(
        sgid=None,
        sg_name=None,
        ssh_port=22,
        disable_current=False,
    )
