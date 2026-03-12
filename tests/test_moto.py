import boto3

from moto import mock_aws


# Tests of Moto
# One of these was failing, passes now.

@mock_aws
def test_security_group_ingress_succeeds():
    ec2 = boto3.resource('ec2', 'ca-central-1')
    sg = ec2.create_security_group(Description='Test SG', GroupName='test-sg')

    assert len(sg.ip_permissions) == 0
    sg.authorize_ingress(IpPermissions=[
        {
            'FromPort': 22,
            'ToPort': 22,
            'IpProtocol': 'tcp',
            'IpRanges': [
                {
                    'CidrIp': '192.168.0.1/32'
                }
            ]
        }
    ])

    assert len(sg.ip_permissions) == 1

    sg_after = ec2.SecurityGroup(sg.id)
    assert len(sg_after.ip_permissions) == 1


@mock_aws
def test_security_group_ingress_fails_without_multirule():
    ec2 = boto3.resource('ec2', 'ca-central-1')
    sg = ec2.create_security_group(Description='Test SG', GroupName='test-sg')

    assert len(sg.ip_permissions) == 0
    sg.authorize_ingress(CidrIp='192.168.0.1/32', FromPort=22, ToPort=22, IpProtocol='tcp')

    # Used to Fail
    assert len(sg.ip_permissions) == 1


@mock_aws
def test_security_group_ingress_fails_without_multirule_after_reload():
    ec2 = boto3.resource('ec2', 'ca-central-1')
    sg = ec2.create_security_group(Description='Test SG', GroupName='test-sg')

    assert len(sg.ip_permissions) == 0
    sg.authorize_ingress(CidrIp='192.168.0.1/32', FromPort=22, ToPort=22, IpProtocol='tcp')

    # Also Fails
    sg_after = ec2.SecurityGroup(sg.id)
    assert len(sg_after.ip_permissions) == 1


@mock_aws
def test_security_group_ipv6_ingress_succeeds():
    ec2 = boto3.resource('ec2', 'ca-central-1')
    sg = ec2.create_security_group(Description='Test SG', GroupName='test-sg')

    assert len(sg.ip_permissions) == 0
    sg.authorize_ingress(IpPermissions=[{
        'FromPort': 22,
        'ToPort': 22,
        'IpProtocol': 'tcp',
        'Ipv6Ranges': [{'CidrIpv6': '2001:db8::/32'}]
    }])

    sg_after = ec2.SecurityGroup(sg.id)
    assert len(sg_after.ip_permissions) == 1
    assert sg_after.ip_permissions[0]['Ipv6Ranges'] == [{'CidrIpv6': '2001:db8::/32'}]


@mock_aws
def test_security_group_ipv6_ingress_revoke_succeeds():
    ec2 = boto3.resource('ec2', 'ca-central-1')
    sg = ec2.create_security_group(Description='Test SG', GroupName='test-sg')

    sg.authorize_ingress(IpPermissions=[{
        'FromPort': 22,
        'ToPort': 22,
        'IpProtocol': 'tcp',
        'Ipv6Ranges': [{'CidrIpv6': '2001:db8::/32'}]
    }])

    sg.revoke_ingress(IpPermissions=[{
        'FromPort': 22,
        'ToPort': 22,
        'IpProtocol': 'tcp',
        'Ipv6Ranges': [{'CidrIpv6': '2001:db8::/32'}]
    }])

    sg_after = ec2.SecurityGroup(sg.id)
    assert len(sg_after.ip_permissions) == 0
