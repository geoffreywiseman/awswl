import argparse
import os

AWSWL_SGID_KEY = 'AWSWL_SGID'
AWSWL_SGNAME_KEY = 'AWSWL_SGNAME'


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Maintains a list of allowlisted CIDR blocks granted SSH access to '
                    'AWS via a security group.'
    )

    # Top-Level Options
    sg_group = parser.add_mutually_exclusive_group(required=False)
    sg_group.add_argument(
        '--sgid', default=os.environ.get(AWSWL_SGID_KEY),
        help='The security group to use for SSH access.'
    )
    sg_group.add_argument(
        '--sg-name', default=os.environ.get(AWSWL_SGNAME_KEY),
        help='The name of the security group to use (wildcards allowed).'
    )
    parser.add_argument(
        '--ssh-port', default=22,
        help='The port used for SSH. By default this is port 22, but some people '
             'prefer to access SSH over another port.'
    )

    # Subcommands
    subparser = parser.add_subparsers(dest='command', help='Subcommands to control the allowlist.')

    subparser.add_parser('version', help='Displays the current version of awswl.')
    subparser.add_parser('list', help='Lists the ip addresses in the security group with SSH access.')

    # Remove
    remove_parser = subparser.add_parser('remove', help="Removes a manually-specified CIDR block from the allowlist.")
    remove_parser.add_argument('cidrs', nargs='+', help="The CIDR blocks to remove from the allowlist.")
    subparser.add_parser('remove-current', help='Remove the current IP address from the allowlist.')

    # Add
    add_parser = subparser.add_parser('add', help="Adds one or more manually-specified CIDR block from the allowlist.")
    add_parser.add_argument('cidrs', nargs='+', help="The CIDR block(s) to add.")
    addcurrent_parser = subparser.add_parser( 'add-current', help='Adds the current IP address to the allowlist.' )
    for sp in [add_parser, addcurrent_parser]:
        desc_group = sp.add_mutually_exclusive_group()
        desc_group.add_argument(
            "--desc", help="Specify a description to use for all added CIDRs."
        )
        desc_group.add_argument(
            "--auto-desc", action="store_true",
            help="Automatically generate a description to use for all added CIDRs."
        )

    ## Update
    update_parser = subparser.add_parser('update', help="Updates the CIDR associated with a specified description in the allowlist.")
    update_parser.add_argument('--desc', help="The description already in the allowlist associated with the rule you want to update.", required=True)
    update_parser.add_argument( 'cidr', help="The new CIDR block to associate with the specified description." )
    update_parser = subparser.add_parser('update-current', help="Updates the CIDR associated with a specified description to the current IP address.")
    update_parser.add_argument('--desc', help="The description already in the allowlist associated with the rule you want to update.", required=True)

    return parser.parse_args(args)
