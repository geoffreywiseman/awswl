import argparse
import os

AWSWL_SGID_KEY = 'AWSWL_SGID'


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Maintains a list of whitelisted CIDR blocks granted SSH access to AWS via a '
                    'security group.'
    )
    parser.add_argument(
        '--list', action='append_const', dest='actions', const='cmd_list',
        help='Lists the ip addresses in the security group with SSH access.'
    )
    parser.add_argument(
        '--add-current', action='append_const', dest='actions', const='cmd_add_current',
        help='Adds the current IP address to the whitelist.'
    )
    parser.add_argument(
        '--remove-current', action='append_const', dest='actions', const='cmd_remove_current',
        help='Remove the current IP address from the whitelist.'
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
        '--ssh-port', default=22,
        help='The port used for SSH. By default this is port 22, but some people '
             'prefer to access SSH over another port.'
    )
    parser.add_argument(
        '--add', action='append', dest='add_blocks',
        help="Adds a manually-specified CIDR block from the whitelist."
    )
    parser.add_argument(
        '--remove', action='append', dest='remove_blocks',
        help="Removes a manually-specified CIDR block from the whitelist."
    )

    return parser.parse_args(args)
