import sys

from . import cli, commands
from pkg_resources import resource_string


def main():
    args = sys.argv[1:]
    options = cli.parse_args(args)
    version = resource_string(__name__, 'VERSION').decode('utf8').strip()
    options.version = version
    execute(options)


def execute(options):
    if validate_options(options):
        if options.actions:
            for command_name in options.actions:
                command = getattr(commands, command_name)
                if command:
                    command(options)
                else:
                    print("Unexpected command: {0}".format(command_name))
        if options.add_blocks:
            for cidr_block in options.add_blocks:
                commands.cmd_add(options,cidr_block)


def validate_options(options):
    if not options.sgid:
        print(
            "No security group specified as an argument with --sgid or in the environment "
            "as AWSWL_SGID. Cannot proceed.")
        return False
    elif not options.actions and not options.add_blocks:
        print(
            "You haven't asked AWSWL to do anything. Try `awswl --help` to get started?.")
        return False
    return True
