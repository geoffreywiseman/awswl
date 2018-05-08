from __future__ import unicode_literals
from builtins import dict, str

import boto3
import botocore

from ipaddress import ip_network, ip_address
from botocore.exceptions import ClientError


from . import externalip


def cmd_list(options):
    external_ip = ip_address(str(externalip.get_external_ip()))
    try:
        ec2 = boto3.resource('ec2')
        security_group = ec2.SecurityGroup(options.sgid)

        ssh_permissions = [
            permission
            for permission in security_group.ip_permissions
            if permission['IpProtocol'] == 'tcp' and
               permission['ToPort'] <= options.ssh_port <= permission['FromPort']
        ]
        authorized_blocks = [
            ip_network(str(ip_range['CidrIp']))
            for permission in ssh_permissions
            for ip_range in permission['IpRanges']
        ]
        authorized_blocks += [
            ip_network(str(ip_range['CidrIpv6']))
            for permission in ssh_permissions
            if 'Ipv6Ranges' in permission
            for ip_range in permission['Ipv6Ranges']
        ]
        if authorized_blocks:
            print("The following CIDR blocks are authorized for SSH:")
            for block in authorized_blocks:
                if external_ip in block:
                    print("- {0} (current)".format(block))
                else:
                    print("- {0}".format(block))
        else:
            print("No CIDR blocks authorized for SSH.")
        print("")
    except botocore.exceptions.NoRegionError:
        print("No AWS region specified (AWS configuration/environment variables).")
    except ClientError as e:
        print(e)


def cmd_add_current(options):
    external_ip = externalip.get_external_ip()
    cidr = "{0}/32".format(external_ip)
    add_cidr(options, "current external IP address as a", cidr)


def add_cidr(options, description, cidr):
    try:
        ec2 = boto3.resource('ec2')
        security_group = ec2.SecurityGroup(options.sgid)

        security_group.authorize_ingress(
            # FIXME: Workaround for Moto issue: https://github.com/spulec/moto/issues/1522
            # CidrIp=cidr,
            # IpProtocol='tcp',
            # FromPort=options.ssh_port,
            # ToPort=options.ssh_port
            IpPermissions=[
                {
                    'IpRanges': [{'CidrIp': cidr}],
                    'IpProtocol': 'tcp',
                    'FromPort': options.ssh_port,
                    'ToPort': options.ssh_port,
                }
            ]
        )
        print("Added {0} CIDR block ({1}) to whitelist.".format(description, cidr))
    except ClientError as e:
        if e.response['Error']['Code'] == "InvalidPermission.Duplicate":
            cap_desc = description[0].capitalize() + description[1:]
            print("{0} is already whitelisted.".format(cap_desc))
        else:
            print(e)


def cmd_remove_current(options):
    external_ip = externalip.get_external_ip()
    cidr = "{0}/32".format(external_ip)
    remove_cidr(options, "current external IP address as a", cidr)


def remove_cidr(options, description, cidr):
    try:
        ec2 = boto3.resource('ec2')
        security_group = ec2.SecurityGroup(options.sgid)
        security_group.revoke_ingress(
            # FIXME: Workaround for Moto issue: https://github.com/spulec/moto/issues/1522
            # CidrIp=cidr,
            # IpProtocol='tcp',
            # FromPort=options.ssh_port,
            # ToPort=options.ssh_port
            IpPermissions=[
                {
                    'IpRanges': [{'CidrIp': cidr}],
                    'IpProtocol': 'tcp',
                    'FromPort': options.ssh_port,
                    'ToPort': options.ssh_port,
                }
            ]
        )
        print("Removed {0} CIDR block ({1}) from whitelist.".format(description, cidr))
    except ClientError as e:
        if e.response['Error']['Code'] == "InvalidPermission.NotFound":
            cap_desc = description[0].capitalize() + description[1:]
            print("{0} CIDR block does not seem to be whitelisted.".format(cap_desc))
        else:
            print(e)


def cmd_version(options):
    print("awswl v{0}".format(options.version))


def cmd_add(options, cidr_block):
    try:
        network = ip_network(str(cidr_block), strict=False)
        add_cidr(options, "specified", network.compressed)
    except ValueError as e:
        print("Add error: {0}\n".format(str(e)))
        return


def cmd_remove(options, cidr_block):
    try:
        network = ip_network(str(cidr_block), strict=False)
        remove_cidr(options, "specified", network.compressed)
    except ValueError as e:
        print("Remove error: {0}\n".format(str(e)))
        return
