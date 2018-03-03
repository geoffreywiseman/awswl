import argparse
import os

AWSWL_SGID_KEY='AWSWL_SGID'

def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Maintains a list of whitelisted CIDR blocks granted SSH access to AWS via a '
                    'security group.'
    )
    parser.add_argument(
        '--list', action='append_const', dest='actions', const='list',
        help='Lists the ip addresses in the security group with SSH access.'
    )
    parser.add_argument(
        '--add-current', action='append_const', dest='actions', const='add_current',
        help='Adds the current IP address to the whitelist.'
    )
    parser.add_argument(
        '--remove-current', action='append_const', dest='actions', const='remove_current',
        help='Remove the current IP address from the whitelist.'
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
    # TODO: What happens if store_const is called twice for the same dest?
    # TODO: Add, Remove, A:qdd Current, Remove Current
    return parser.parse_args(args)
