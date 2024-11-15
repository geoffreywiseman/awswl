import sys
from argparse import Namespace

from . import cli, commands


def main():
    args = sys.argv[1:]
    if not args:
        args = ['--help']
    options = cli.parse_args(args)
    execute(options)


def execute(options: Namespace):
    if not validate_options(options):
        return

    cmd_name = f"cmd_{options.command.replace('-', '_')}"
    if hasattr(commands, cmd_name):
        command_fn = getattr(commands, cmd_name)
        command_fn(options)
    else:
        print(f"Unexpected command: {options.command}")


def validate_options(options: Namespace):
    if options.command != 'version' and not options.sgid and not options.sg_name:
        print(
            "You must specify a security group id (--sgid option, AWSWL_SGID env var) "
            "or security group name (--sg-name, AWSWL_SGNAME) for awswl to use."
        )
        return False
    return True
