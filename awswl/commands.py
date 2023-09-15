import os
from argparse import Namespace
from builtins import str
from datetime import datetime
from typing import Optional

import boto3
import botocore

from ipaddress import ip_network, ip_address
from botocore.exceptions import ClientError

from . import externalip


def cmd_list(options):
    external_ip = ip_address(str(externalip.get_external_ip()))
    try:
        security_group = get_security_group(options)
        if not security_group:
            return

        ssh_permissions = [
            permission
            for permission in security_group.ip_permissions
            if permission['IpProtocol'] == 'tcp' and
               permission['ToPort'] <= options.ssh_port <= permission['FromPort']
        ]
        authorized_blocks = [
            [ip_network(str(ip_range['CidrIp'])), ip_range.get('Description')]
            for permission in ssh_permissions
            for ip_range in permission['IpRanges']
        ]
        authorized_blocks += [
            [ip_network(str(ip_range['CidrIpv6'])), ip_range.get('Description')]
            for permission in ssh_permissions
            if 'Ipv6Ranges' in permission
            for ip_range in permission['Ipv6Ranges']
        ]
        if authorized_blocks:
            print("The following CIDR blocks are authorized for SSH:")
            for block, desc in authorized_blocks:
                current = external_ip in block
                print(f"- {str(block):35}{'(current)' if current else ''}{'(' + desc + ')' if desc else ''}")
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
    add_cidr(options, "current external IP address as a CIDR block", cidr, get_description(options))


def get_description(options: Namespace) -> Optional[str]:
    if 'auto_desc' in options and options.auto_desc:
        return get_auto_description()
    elif 'desc' in options and options.desc:
        return options.desc
    else:
        return None


def get_auto_description():
    return f"{os.getlogin()} - {datetime.now().date()}"


def add_cidr(options, explain, cidr, description):
    try:
        security_group = get_security_group(options)
        if security_group:
            ip_range = dict()
            ip_range['CidrIp'] = cidr
            if description:
                ip_range['Description'] = description
            security_group.authorize_ingress(
                IpPermissions=[
                    {
                        'IpRanges': [ip_range],
                        'IpProtocol': 'tcp',
                        'FromPort': options.ssh_port,
                        'ToPort': options.ssh_port
                    }
                ]
            )
            print("Added {0} ({1}) to allowlist.".format(explain, cidr))
    except ClientError as e:
        if e.response['Error']['Code'] == "InvalidPermission.Duplicate":
            cap_desc = description[0].capitalize() + description[1:]
            print("{0} is already allowlisted.".format(cap_desc))
        else:
            print("Unexpected error")
            print(e)


def cmd_remove_current(options):
    external_ip = externalip.get_external_ip()
    cidr = "{0}/32".format(external_ip)
    remove_cidr(options, "current external IP address as a CIDR block", cidr)


def remove_cidr(options, description, cidr):
    try:
        security_group = get_security_group(options)
        if security_group:
            security_group.revoke_ingress(
                CidrIp=cidr,
                IpProtocol='tcp',
                FromPort=options.ssh_port,
                ToPort=options.ssh_port
            )
            print("Removed {0} ({1}) from allowlist.".format(description, cidr))
    except ClientError as e:
        if e.response['Error']['Code'] == "InvalidPermission.NotFound":
            cap_desc = description[0].capitalize() + description[1:]
            print("{0} does not seem to be allowlisted.".format(cap_desc))
        else:
            print(e)


def cmd_version(options):
    print("awswl v{0}".format(options.version))


def cmd_add(options, cidr_block):
    try:
        network = ip_network(str(cidr_block), strict=False)
        add_cidr(options, "specified CIDR block", network.compressed, get_description(options))
    except ValueError as e:
        print("Add error: {0}\n".format(str(e)))
        return


def cmd_remove(options, cidr_block):
    try:
        network = ip_network(str(cidr_block), strict=False)
        remove_cidr(options, "specified CIDR block", network.compressed)
    except ValueError as e:
        print("Remove error: {0}\n".format(str(e)))
        return


def get_security_group(options: Namespace):
    ec2 = boto3.resource('ec2')
    if options.sgid:
        return ec2.SecurityGroup(options.sgid)
    else:
        groups = get_matching_security_groups(options.sg_name)
        if len(groups) == 0:
            print(f"Could not find security group with name {options.sg_name}\n")
        elif len(groups) == 1:
            [name, sgid] = groups[0]
            print(f"Using security group {name} ({sgid}).\n")
            return ec2.SecurityGroup(sgid)
        else:
            print(f"Found {len(groups)} security groups matching name: ")
            for group in groups:
                print(f"- {group[0]} ({group[1]})")


def get_matching_security_groups(sg_name):
    groups = []
    pager = boto3.client('ec2').get_paginator('describe_security_groups')
    # search security groups by name
    for page in pager.paginate(Filters=[{'Name': 'group-name', 'Values': [sg_name]}]):
        # append sgid to groups list
        for group in page['SecurityGroups']:
            groups.append([group['GroupName'], group['GroupId']])
    return groups
