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


@pytest.fixture(name='options')
def options_fixture():
    """Return a factory that builds a Namespace with CLI defaults, overridable via kwargs."""
    def _make(**kwargs):
        return Namespace(
            command=kwargs.get('command'),
            sgid=kwargs.get('sgid'),
            sg_name=kwargs.get('sg_name'),
            ssh_port=kwargs.get('ssh_port', 22),
            auto_desc=kwargs.get('auto_desc', False),
            desc=kwargs.get('desc'),
            cidrs=kwargs.get('cidrs', []),
            cidr=kwargs.get('cidr'),
            disable_current=kwargs.get('disable_current', False),
        )
    return _make
