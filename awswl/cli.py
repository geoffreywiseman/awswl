import argparse
import os

AWSWL_SGID_KEY = 'AWSWL_SGID'
AWSWL_SGNAME_KEY = 'AWSWL_SGNAME'


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Maintains a list of allowlisted CIDR blocks granted SSH access to '
                    'AWS via a security group.'
    )
    parser.add_argument(
        '--list', action='append_const', dest='actions', const='cmd_list',
        help='Lists the ip addresses in the security group with SSH access.'
    )
    parser.add_argument(
        '--add-current', action='append_const', dest='actions', const='cmd_add_current',
        help='Adds the current IP address to the allowlist.'
    )
    parser.add_argument(
        '--remove-current', action='append_const', dest='actions',
        const='cmd_remove_current',
        help='Remove the current IP address from the allowlist.'
    )
    parser.add_argument(
        '--version', action='append_const', dest='actions', const='cmd_version',
        help='Print the current version of awswl.'
    )
    parser.add_argument(
        '--sgid', default=os.environ.get(AWSWL_SGID_KEY),
        help='The security group to use for SSH access.'
    )
    parser.add_argument(
        '--sg-name', default=os.environ.get(AWSWL_SGNAME_KEY),
        help='The name of the security group to use (wildcards allowed).'
    )
    parser.add_argument(
        '--ssh-port', default=22,
        help='The port used for SSH. By default this is port 22, but some people '
             'prefer to access SSH over another port.'
    )
    parser.add_argument(
        '--add', action='append', dest='add_blocks',
        help="Adds a manually-specified CIDR block from the allowlist."
    )
    parser.add_argument(
        '--remove', action='append', dest='remove_blocks',
        help="Removes a manually-specified CIDR block from the allowlist."
    )

    # Descriptions
    desc_group = parser.add_mutually_exclusive_group()
    desc_group.add_argument(
        "--desc", help="Specify a description to use for all added CIDRs."
    )
    desc_group.add_argument(
        "--auto-desc", action="store_true",
        help="Automatically generate a description for all added CIDRs."
    )

    return parser.parse_args(args)
