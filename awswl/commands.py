import boto3
import botocore

from ipaddress import ip_network, ip_address
from botocore.exceptions import ClientError

from . import externalip


def cmd_list(options):
    external_ip = ip_address(externalip.get_external_ip())
    try:
        ec2 = boto3.resource('ec2')
        security_group = ec2.SecurityGroup(options.sgid)
        ssh_permissions = [
            permission
            for permission in security_group.ip_permissions
            if permission['IpProtocol'] == 'tcp' and permission['ToPort'] == options.ssh_port
        ]
        authorized_blocks = [
            ip_network(ip_range['CidrIp'])
            for permission in ssh_permissions
            for ip_range in permission['IpRanges']
        ]
        authorized_blocks += [
            ip_network(ip_range['CidrIpv6'])
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
    except botocore.exceptions.NoRegionError:
        print("No AWS region specified (AWS configuration/environment variables).")
    except ClientError as e:
        print(e)


def cmd_add_current(options):
    try:
        external_ip = externalip.get_external_ip()
        cidr = "{0}/32".format(external_ip)
        ec2 = boto3.resource('ec2')
        security_group = ec2.SecurityGroup(options.sgid)
        security_group.authorize_ingress(
            CidrIp=cidr,
            IpProtocol='tcp',
            FromPort=options.ssh_port,
            ToPort=options.ssh_port
        )
        print("Added current ip address as a CIDR block ({0}) to whitelist.".format(cidr))
    except ClientError as e:
        if e.response['Error']['Code'] == "InvalidPermission.Duplicate":
            print("Current IP address is already whitelisted.")
        else:
            print(e)


def cmd_remove_current(options):
    try:
        external_ip = externalip.get_external_ip()
        cidr = "{0}/32".format(external_ip)
        ec2 = boto3.resource('ec2')
        security_group = ec2.SecurityGroup(options.sgid)
        security_group.revoke_ingress(
            CidrIp=cidr,
            IpProtocol='tcp',
            FromPort=options.ssh_port,
            ToPort=options.ssh_port
        )
        print("Removed current ip address as a CIDR block ({0}) from whitelist.".format(cidr))
    except ClientError as e:
        if e.response['Error']['Code'] == "InvalidPermission.Duplicate":
            print("Current IP address is already whitelisted.")
        else:
            print(e)


def cmd_version(options):
    print("awswl v{0}".format(options.version))
