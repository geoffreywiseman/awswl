import sys
from argparse import Namespace

from . import cli, commands
from pkg_resources import get_distribution


def main():
    args = sys.argv[1:]
    options = cli.parse_args(args)
    version = get_distribution('awswl').version
    options.version = version
    execute(options)


def execute(options: Namespace):
    if validate_options(options):
        if options.actions:
            for command_name in options.actions:
                command = getattr(commands, command_name)
                if command:
                    command(options)
                else:
                    print(f"Unexpected command: {command_name}")
        if options.add_blocks:
            for cidr_block in options.add_blocks:
                commands.cmd_add(options, cidr_block)
        if options.remove_blocks:
            for cidr_block in options.remove_blocks:
                commands.cmd_remove(options, cidr_block)


def has_action(options: Namespace):
    return not options.actions and \
        not options.add_blocks and \
        not options.remove_blocks


def validate_options(options):
    if not options.sgid and not options.sg_name:
        print(
            "You must specify a security group id (--sgid option, AWSWL_SGID env var) "
            "or security group name (--sg-name, AWSWL_SGNAME) for awswl to use."
        )
        return False
    elif has_action(options):
        print(
            "You haven't asked AWSWL to do anything. "
            "Try `awswl --help` to get started?"
        )
        return False
    return True
