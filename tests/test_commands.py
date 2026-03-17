import os
from argparse import Namespace
from datetime import date
from unittest.mock import patch

import boto3
from moto import mock_aws

import awswl
from awswl import commands


def options(**kwargs):
    opt = Namespace()
    opt.sgid = kwargs.get('sgid')
    opt.sg_name = kwargs.get('sg_name')
    opt.ssh_port = 22
    opt.auto_desc = kwargs.get('auto_desc')
    opt.desc = kwargs.get('desc')
    opt.cidrs = kwargs.get('cidrs', [])
    opt.cidr = kwargs.get('cidr')
    opt.disable_current = kwargs.get('disable_current', False)
    return opt


def assert_list_output(opt, matches, capsys):
    with patch('awswl.externalip.get_external_ip', return_value='192.0.2.1'):
        commands.cmd_list(opt)
    output = capsys.readouterr().out
    if isinstance(matches, str):
        assert matches in output, f"Cannot find '{matches}' in output: {output}"
    if isinstance(matches, list):
        for match in matches:
            assert match in output, f"Cannot find '{match}' in output: {output}"


def test_version_command(capsys):
    commands.cmd_version(Namespace())
    assert capsys.readouterr().out == f"awswl v{awswl.version}\n"


def test_list_command_lists_no_blocks_sgid(region, security_group, capsys):
    assert_list_output(options(sgid=security_group.id), "No CIDR blocks authorized for SSH", capsys)


def test_list_command_lists_no_blocks_sgname(region, security_group, capsys):
    assert_list_output(options(sg_name=security_group.group_name), "No CIDR blocks authorized for SSH", capsys)


def test_list_command_lists_ipv4_blocks(region, security_group, capsys):
    security_group.authorize_ingress(IpPermissions=[{
        'IpRanges': [
            {'CidrIp': '10.0.0.1/32'},
            {'CidrIp': '10.0.1.0/24'}
        ],
        'IpProtocol': 'tcp',
        'FromPort': 22,
        'ToPort': 22
    }])
    assert_list_output(options(sgid=security_group.id), ["- 10.0.0.1/32", "- 10.0.1.0/24"], capsys)
    assert_list_output(options(sg_name=security_group.group_name), ["- 10.0.0.1/32", "- 10.0.1.0/24"], capsys)


def test_list_command_lists_ipv6_blocks(region, security_group, capsys):
    security_group.authorize_ingress(IpPermissions=[{
        'Ipv6Ranges': [
            {'CidrIpv6': '2001:db8::/32'},
            {'CidrIpv6': '2001:db8:1::/48'}
        ],
        'IpProtocol': 'tcp',
        'FromPort': 22,
        'ToPort': 22
    }])
    assert_list_output(options(sgid=security_group.id), ["- 2001:db8::/32", "- 2001:db8:1::/48"], capsys)
    assert_list_output(options(sg_name=security_group.group_name), ["- 2001:db8::/32", "- 2001:db8:1::/48"], capsys)


def test_list_command_lists_descriptions(region, security_group, capsys):
    security_group.authorize_ingress(IpPermissions=[{
        'IpRanges': [
            {'CidrIp': '10.0.0.1/32', 'Description': 'Double Trouble'},
            {'CidrIp': '10.0.1.0/24'},
            {'CidrIp': '192.168.0.0/16', 'Description': 'Sweet Sixteen'}
        ],
        'IpProtocol': 'tcp',
        'FromPort': 22,
        'ToPort': 22
    }])
    assert_list_output(
        options(sgid=security_group.id), [
            "- 10.0.0.1/32                        (Double Trouble)\n",
            "- 10.0.1.0/24                        \n",
            "- 192.168.0.0/16                     (Sweet Sixteen)\n",
        ],
        capsys
    )
    assert_list_output(
        options(sg_name=security_group.group_name), [
            "- 10.0.0.1/32                        (Double Trouble)\n",
            "- 10.0.1.0/24                        \n",
            "- 192.168.0.0/16                     (Sweet Sixteen)\n",
        ],
        capsys
    )


def test_list_command_identifies_enclosing_blocks(region, security_group, capsys):
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
        options(sgid=security_group.id), [
            "- 192.0.2.1/32                       (current)\n",
            "- 192.0.2.0/24                       (current)\n",
            "- 192.0.1.0/24                       \n"
        ],
        capsys
    )
    assert_list_output(
        options(sg_name=security_group.group_name),
        [
            "- 192.0.2.1/32                       (current)\n",
            "- 192.0.2.0/24                       (current)\n",
            "- 192.0.1.0/24                       \n"
        ],
        capsys
    )


@mock_aws
def test_list_command_sg_not_found(region, capsys):
    """When the named security group does not exist, cmd_list exits without printing blocks."""
    opt = options(sg_name='nonexistent-sg')
    with patch('awswl.externalip.get_external_ip', return_value='192.0.2.1'):
        commands.cmd_list(opt)
    assert "Could not find security group" in capsys.readouterr().out


@mock_aws
def test_list_command_multiple_sgs_found(region, capsys):
    """When multiple security groups share a name, cmd_list lists them and exits."""
    ec2 = boto3.resource('ec2', region_name=region)
    ec2.create_security_group(Description='First', GroupName='dup-sg', VpcId='vpc-111')
    ec2.create_security_group(Description='Second', GroupName='dup-sg', VpcId='vpc-222')
    opt = options(sg_name='dup-sg')
    with patch('awswl.externalip.get_external_ip', return_value='192.0.2.1'):
        commands.cmd_list(opt)
    output = capsys.readouterr().out
    assert "Found 2 security groups matching name:" in output


def test_list_command_no_region_shows_error(capsys, monkeypatch):
    """cmd_list prints a clear message when no AWS region is configured."""
    monkeypatch.delenv('AWS_DEFAULT_REGION', raising=False)
    monkeypatch.setenv('AWS_CONFIG_FILE', '/dev/null')
    opt = options(sgid='sg-12345')
    with patch('awswl.externalip.get_external_ip', return_value='192.0.2.1'):
        commands.cmd_list(opt)
    assert "No AWS region specified" in capsys.readouterr().out


def test_add_current_adds_permission(region, security_group, capsys):
    assert not security_group.ip_permissions
    opt = options(sgid=security_group.id)
    with patch('awswl.externalip.get_external_ip', return_value='192.0.2.1'):
        commands.cmd_add_current(opt)

    after_group = boto3.resource('ec2').SecurityGroup(security_group.id)
    assert len(after_group.ip_permissions) == 1
    ranges = after_group.ip_permissions[0]['IpRanges']
    assert len(ranges) == 1
    assert ranges[0]['CidrIp'] == '192.0.2.1/32'
    assert "Added current external IP address as a CIDR block" in capsys.readouterr().out


def test_add_adds_specified_permission_sgid(region, security_group, capsys):
    assert not security_group.ip_permissions
    opt = options(sgid=security_group.id, cidrs=['192.0.2.1/24'])
    commands.cmd_add(opt)

    after_group = boto3.resource('ec2').SecurityGroup(security_group.id)
    assert len(after_group.ip_permissions) == 1
    ranges = after_group.ip_permissions[0]['IpRanges']
    assert len(ranges) == 1
    assert ranges[0]['CidrIp'] == '192.0.2.0/24'
    assert "Added specified CIDR block" in capsys.readouterr().out


def test_add_adds_specified_permission_sgname(region, security_group, capsys):
    assert not security_group.ip_permissions
    opt = options(sg_name=security_group.group_name, cidrs=['192.0.2.1/24'])
    commands.cmd_add(opt)

    after_group = boto3.resource('ec2').SecurityGroup(security_group.id)
    assert len(after_group.ip_permissions) == 1
    ranges = after_group.ip_permissions[0]['IpRanges']
    assert len(ranges) == 1
    assert ranges[0]['CidrIp'] == '192.0.2.0/24'
    assert "Added specified CIDR block" in capsys.readouterr().out


def test_add_explicit_desc(region, security_group, capsys):
    """Explicit --desc is stored on the added rule and echoed in the output."""
    opt = options(sgid=security_group.id, cidrs=['10.0.0.1/32'], desc='my-description')
    commands.cmd_add(opt)

    after_group = boto3.resource('ec2').SecurityGroup(security_group.id)
    ranges = after_group.ip_permissions[0]['IpRanges']
    assert ranges[0]['Description'] == 'my-description'
    assert "my-description" in capsys.readouterr().out


def test_add_invalid_cidr_shows_error(region, security_group, capsys):
    """An invalid CIDR string produces an 'Add error' message instead of crashing."""
    opt = options(sgid=security_group.id, cidrs=['not-a-valid-cidr'])
    commands.cmd_add(opt)
    assert "Add error:" in capsys.readouterr().out


def test_add_adds_specified_ipv6_permission(region, security_group, capsys):
    assert not security_group.ip_permissions
    opt = options(sgid=security_group.id, cidrs=['2001:db8::/32'])
    commands.cmd_add(opt)

    after_group = boto3.resource('ec2').SecurityGroup(security_group.id)
    assert len(after_group.ip_permissions) == 1
    ipv6_ranges = after_group.ip_permissions[0]['Ipv6Ranges']
    assert len(ipv6_ranges) == 1
    assert ipv6_ranges[0]['CidrIpv6'] == '2001:db8::/32'
    assert "Added specified CIDR block" in capsys.readouterr().out


def test_add_ipv6_when_already_present(region, security_group, capsys):
    security_group.authorize_ingress(IpPermissions=[{
        'Ipv6Ranges': [{'CidrIpv6': '2001:db8::/32'}],
        'IpProtocol': 'tcp',
        'FromPort': 22,
        'ToPort': 22
    }])
    opt = options(sgid=security_group.id, cidrs=['2001:db8::/32'])
    commands.cmd_add(opt)

    after_group = boto3.resource('ec2').SecurityGroup(security_group.id)
    assert len(after_group.ip_permissions) == 1
    assert len(after_group.ip_permissions[0]['Ipv6Ranges']) == 1
    assert "already allowlisted" in capsys.readouterr().out


def test_add_ipv6_when_containing_rule_present(region, security_group, capsys):
    security_group.authorize_ingress(IpPermissions=[{
        'Ipv6Ranges': [{'CidrIpv6': '2001:db8::/32'}],
        'IpProtocol': 'tcp',
        'FromPort': 22,
        'ToPort': 22
    }])
    opt = options(sgid=security_group.id, cidrs=['2001:db8:1::/48'])
    commands.cmd_add(opt)

    after_group = boto3.resource('ec2').SecurityGroup(security_group.id)
    assert len(after_group.ip_permissions) == 1
    assert len(after_group.ip_permissions[0]['Ipv6Ranges']) == 1
    assert "already covered by existing rule" in capsys.readouterr().out


def test_remove_current_removes_permission_sgid(region, security_group, capsys):
    security_group.authorize_ingress(IpPermissions=[{
        'IpRanges': [{'CidrIp': '192.0.2.4/32'}],
        'IpProtocol': 'tcp',
        'FromPort': 22,
        'ToPort': 22
    }])
    opt = options(sgid=security_group.id)
    with patch('awswl.externalip.get_external_ip', return_value='192.0.2.4'):
        commands.cmd_remove_current(opt)

    after_group = boto3.resource('ec2').SecurityGroup(security_group.id)
    assert not after_group.ip_permissions
    assert "Removed current external IP address (192.0.2.4/32)" in capsys.readouterr().out


def test_remove_current_removes_permission_sgname(region, security_group, capsys):
    security_group.authorize_ingress(IpPermissions=[{
        'IpRanges': [{'CidrIp': '192.0.2.8/32'}],
        'IpProtocol': 'tcp',
        'FromPort': 22,
        'ToPort': 22
    }])
    opt = options(sg_name=security_group.group_name)
    with patch('awswl.externalip.get_external_ip', return_value='192.0.2.8'):
        commands.cmd_remove_current(opt)

    after_group = boto3.resource('ec2').SecurityGroup(security_group.id)
    assert not after_group.ip_permissions
    assert "Removed current external IP address (192.0.2.8/32)" in capsys.readouterr().out


def test_remove_current_indicates_notfound_sgid(region, security_group, capsys):
    opt = options(sgid=security_group.id)
    with patch('awswl.externalip.get_external_ip', return_value='192.0.2.1'):
        commands.cmd_remove_current(opt)
    assert "Current external IP address (192.0.2.1/32) does not seem to be allowlisted." \
           in capsys.readouterr().out


def test_remove_current_indicates_notfound_sgname(region, security_group, capsys):
    opt = options(sg_name=security_group.group_name)
    with patch('awswl.externalip.get_external_ip', return_value='192.0.2.1'):
        commands.cmd_remove_current(opt)
    assert "Current external IP address (192.0.2.1/32) does not seem to be allowlisted." \
           in capsys.readouterr().out


def test_remove_removes_specified(region, security_group, capsys):
    security_group.authorize_ingress(IpPermissions=[{
        'IpRanges': [{'CidrIp': '192.0.2.1/32'}],
        'IpProtocol': 'tcp',
        'FromPort': 22,
        'ToPort': 22
    }])
    opt = options(sgid=security_group.id, cidrs=['192.0.2.1/32'])
    commands.cmd_remove(opt)

    after_group = boto3.resource('ec2').SecurityGroup(security_group.id)
    assert not after_group.ip_permissions
    assert "Removed 192.0.2.1/32 from allowlist" in capsys.readouterr().out


def test_remove_specified_indicates_notfound(region, security_group, capsys):
    opt = options(sgid=security_group.id, cidrs=['192.0.2.1/32'])
    commands.cmd_remove(opt)
    assert "192.0.2.1/32 does not seem to be allowlisted." in capsys.readouterr().out


def test_remove_invalid_cidr_shows_error(region, security_group, capsys):
    """An invalid CIDR string produces a 'Remove error' message instead of crashing."""
    opt = options(sgid=security_group.id, cidrs=['not-a-valid-cidr'])
    commands.cmd_remove(opt)
    assert "Remove error:" in capsys.readouterr().out


def test_remove_removes_specified_ipv6(region, security_group, capsys):
    security_group.authorize_ingress(IpPermissions=[{
        'Ipv6Ranges': [{'CidrIpv6': '2001:db8::/32'}],
        'IpProtocol': 'tcp',
        'FromPort': 22,
        'ToPort': 22
    }])
    opt = options(sgid=security_group.id, cidrs=['2001:db8::/32'])
    commands.cmd_remove(opt)

    after_group = boto3.resource('ec2').SecurityGroup(security_group.id)
    assert not after_group.ip_permissions
    assert "Removed 2001:db8::/32 from allowlist" in capsys.readouterr().out


def test_remove_specified_ipv6_indicates_notfound(region, security_group, capsys):
    opt = options(sgid=security_group.id, cidrs=['2001:db8::/32'])
    commands.cmd_remove(opt)
    assert "2001:db8::/32 does not seem to be allowlisted." in capsys.readouterr().out


def test_remove_when_ipv6_containing_rule_present(region, security_group, capsys):
    security_group.authorize_ingress(IpPermissions=[{
        'Ipv6Ranges': [{'CidrIpv6': '2001:db8::/32'}],
        'IpProtocol': 'tcp',
        'FromPort': 22,
        'ToPort': 22
    }])
    opt = options(sgid=security_group.id, cidrs=['2001:db8:1::/48'])
    commands.cmd_remove(opt)

    after_group = boto3.resource('ec2').SecurityGroup(security_group.id)
    assert len(after_group.ip_permissions) == 1
    output = capsys.readouterr().out
    assert "2001:db8::/32" in output
    assert "not directly allowlisted" in output


def test_add_current_when_already_present(region, security_group, capsys):
    security_group.authorize_ingress(IpPermissions=[{
        'IpRanges': [
            {'CidrIp': '192.0.2.1/32'},
            {'CidrIp': '192.0.2.2/32'},
        ],
        'IpProtocol': 'tcp',
        'FromPort': 22,
        'ToPort': 22
    }])
    opt = options(sgid=security_group.id)
    with patch('awswl.externalip.get_external_ip', return_value='192.0.2.1'):
        commands.cmd_add_current(opt)

    after_group = boto3.resource('ec2').SecurityGroup(security_group.id)
    assert len(after_group.ip_permissions) == 1
    permission = after_group.ip_permissions[0]
    assert len(permission['IpRanges']) == 2
    assert "already allowlisted" in capsys.readouterr().out


def test_add_current_when_containing_rule_present(region, security_group, capsys):
    security_group.authorize_ingress(IpPermissions=[{
        'IpRanges': [{'CidrIp': '192.0.2.0/24'}],
        'IpProtocol': 'tcp',
        'FromPort': 22,
        'ToPort': 22
    }])
    opt = options(sgid=security_group.id)
    with patch('awswl.externalip.get_external_ip', return_value='192.0.2.1'):
        commands.cmd_add_current(opt)

    after_group = boto3.resource('ec2').SecurityGroup(security_group.id)
    assert len(after_group.ip_permissions) == 1
    permission = after_group.ip_permissions[0]
    assert len(permission['IpRanges']) == 1
    assert "already covered by existing rule" in capsys.readouterr().out


def test_remove_when_containing_rule_present(region, security_group, capsys):
    security_group.authorize_ingress(IpPermissions=[{
        'IpRanges': [{'CidrIp': '192.0.2.0/24'}],
        'IpProtocol': 'tcp',
        'FromPort': 22,
        'ToPort': 22
    }])
    opt = options(sgid=security_group.id, cidrs=['192.0.2.1/32'])
    commands.cmd_remove(opt)

    after_group = boto3.resource('ec2').SecurityGroup(security_group.id)
    assert len(after_group.ip_permissions) == 1
    permission = after_group.ip_permissions[0]
    assert len(permission['IpRanges']) == 1
    output = capsys.readouterr().out
    assert "192.0.2.0/24" in output
    assert "not directly allowlisted" in output


def test_add_autodesc(region, security_group):
    x_acquired = date.fromisoformat("2022-10-27")
    opt = options(sgid=security_group.id, auto_desc=True, cidrs=['1.2.3.4/32'])
    with patch.object(os, 'getlogin', return_value='emusk'), patch('awswl.commands.date') as mock_date:
        mock_date.today.return_value = x_acquired
        commands.cmd_add(opt)

    after_group = boto3.resource('ec2').SecurityGroup(security_group.id)
    assert len(after_group.ip_permissions) == 1
    ranges = after_group.ip_permissions[0]['IpRanges']
    assert len(ranges) == 1
    assert ranges[0]['Description'] == 'emusk - 2022-10-27'


def test_add_desc(region, security_group):
    cwbd = date.fromisoformat("2008-03-01")
    opt = options(sg_name=security_group.group_name, auto_desc=True, cidrs=['3.2.1.0/30'])
    with patch.object(os, 'getlogin', return_value='thestuff'), patch('awswl.commands.date') as mock_date:
        mock_date.today.return_value = cwbd
        commands.cmd_add(opt)

    after_group = boto3.resource('ec2').SecurityGroup(security_group.id)
    assert len(after_group.ip_permissions) == 1
    ranges = after_group.ip_permissions[0]['IpRanges']
    assert len(ranges) == 1
    assert ranges[0]['Description'] == 'thestuff - 2008-03-01'


# ---------------------------------------------------------------------------
# cmd_update / cmd_update_current
# ---------------------------------------------------------------------------

def test_update_command_replaces_cidr(region, security_group, capsys):
    """update finds the rule by description, removes the old CIDR, and adds the replacement."""
    security_group.authorize_ingress(IpPermissions=[{
        'IpRanges': [{'CidrIp': '10.0.0.1/32', 'Description': 'my-host'}],
        'IpProtocol': 'tcp',
        'FromPort': 22,
        'ToPort': 22
    }])
    opt = options(sgid=security_group.id, cidr='10.0.0.2/32', desc='my-host')
    commands.cmd_update(opt)

    after_group = boto3.resource('ec2').SecurityGroup(security_group.id)
    all_cidrs = [r['CidrIp'] for r in after_group.ip_permissions[0]['IpRanges']]
    assert '10.0.0.2/32' in all_cidrs
    assert '10.0.0.1/32' not in all_cidrs
    assert "Added new value" in capsys.readouterr().out


def test_update_command_no_op_when_cidr_unchanged(region, security_group, capsys):
    """update is a no-op and reports 'already allowlisted' when CIDR hasn't changed."""
    security_group.authorize_ingress(IpPermissions=[{
        'IpRanges': [{'CidrIp': '10.0.0.1/32', 'Description': 'my-host'}],
        'IpProtocol': 'tcp',
        'FromPort': 22,
        'ToPort': 22
    }])
    opt = options(sgid=security_group.id, cidr='10.0.0.1/32', desc='my-host')
    commands.cmd_update(opt)
    assert "already allowlisted" in capsys.readouterr().out


def test_update_command_reports_missing_description(region, security_group, capsys):
    """update reports failure when no rule matches the requested description."""
    opt = options(sgid=security_group.id, cidr='10.0.0.2/32', desc='no-such-desc')
    commands.cmd_update(opt)
    assert "no CIDR found matching description" in capsys.readouterr().out


def test_update_invalid_cidr_shows_error(region, security_group, capsys):
    """An invalid CIDR string in update produces an 'Update error' message."""
    # First add a rule so find_cidr_matching_desc would succeed if CIDR were valid.
    security_group.authorize_ingress(IpPermissions=[{
        'IpRanges': [{'CidrIp': '10.0.0.1/32', 'Description': 'my-host'}],
        'IpProtocol': 'tcp',
        'FromPort': 22,
        'ToPort': 22
    }])
    opt = options(sgid=security_group.id, cidr='not-a-valid-cidr', desc='my-host')
    commands.cmd_update(opt)
    assert "Update error:" in capsys.readouterr().out


def test_update_command_reports_duplicate_descriptions(region, security_group, capsys):
    """update reports failure when more than one rule carries the requested description."""
    security_group.authorize_ingress(IpPermissions=[{
        'IpRanges': [
            {'CidrIp': '10.0.0.1/32', 'Description': 'shared-desc'},
            {'CidrIp': '10.0.0.2/32', 'Description': 'shared-desc'},
        ],
        'IpProtocol': 'tcp',
        'FromPort': 22,
        'ToPort': 22
    }])
    opt = options(sgid=security_group.id, cidr='10.0.0.3/32', desc='shared-desc')
    commands.cmd_update(opt)
    assert "found more than one CIDR matching description" in capsys.readouterr().out


def test_update_current_command_replaces_cidr(region, security_group, capsys):
    """update-current finds the rule by description and replaces its CIDR with the current IP."""
    security_group.authorize_ingress(IpPermissions=[{
        'IpRanges': [{'CidrIp': '10.0.0.1/32', 'Description': 'my-host'}],
        'IpProtocol': 'tcp',
        'FromPort': 22,
        'ToPort': 22
    }])
    opt = options(sgid=security_group.id, desc='my-host')
    with patch('awswl.externalip.get_external_ip', return_value='10.0.0.2'):
        commands.cmd_update_current(opt)

    after_group = boto3.resource('ec2').SecurityGroup(security_group.id)
    all_cidrs = [r['CidrIp'] for r in after_group.ip_permissions[0]['IpRanges']]
    assert '10.0.0.2/32' in all_cidrs
    assert '10.0.0.1/32' not in all_cidrs
    assert "Added new value" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# --disable-current
# ---------------------------------------------------------------------------

def test_list_command_disable_current_skips_ip_fetch(region, security_group, capsys):
    """cmd_list with disable_current=True should not call get_external_ip."""
    security_group.authorize_ingress(IpPermissions=[{
        'IpRanges': [{'CidrIp': '192.0.2.1/32'}],
        'IpProtocol': 'tcp',
        'FromPort': 22,
        'ToPort': 22
    }])
    opt = options(sgid=security_group.id, disable_current=True)
    with patch('awswl.externalip.get_external_ip') as mock_get_ip:
        commands.cmd_list(opt)
        mock_get_ip.assert_not_called()
    output = capsys.readouterr().out
    assert "192.0.2.1/32" in output
    assert "(current)" not in output


def test_list_command_disable_current_no_current_marker(region, security_group, capsys):
    """cmd_list with disable_current=True should not mark any block as (current)."""
    security_group.authorize_ingress(IpPermissions=[{
        'IpRanges': [{'CidrIp': '10.0.0.1/32'}],
        'IpProtocol': 'tcp',
        'FromPort': 22,
        'ToPort': 22
    }])
    opt = options(sgid=security_group.id, disable_current=True)
    commands.cmd_list(opt)
    output = capsys.readouterr().out
    assert "10.0.0.1/32" in output
    assert "(current)" not in output
