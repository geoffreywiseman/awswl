from argparse import Namespace
from unittest.mock import patch

import pytest

from awswl import main


def test_unexpected_command(capsys):
    opt = Namespace()
    opt.command = "fubar"
    opt.sgid = "sg-12345"
    opt.sg_name = None
    opt.disable_current = False

    main.execute(opt)

    assert capsys.readouterr().out == "Unexpected command: fubar\n"


def test_execute_requires_security_group(capsys):
    """execute() prints an error and returns when no security group is specified."""
    opt = Namespace()
    opt.command = 'list'
    opt.sgid = None
    opt.sg_name = None
    opt.disable_current = False

    main.execute(opt)

    assert "You must specify a security group" in capsys.readouterr().out


def test_execute_version_skips_sg_check(capsys):
    """The 'version' command bypasses the security-group requirement."""
    opt = Namespace()
    opt.command = 'version'
    opt.sgid = None
    opt.sg_name = None
    opt.disable_current = False

    main.execute(opt)

    assert 'awswl' in capsys.readouterr().out


def test_main_with_version_command(capsys):
    """main() parses sys.argv and dispatches correctly end-to-end."""
    with patch('sys.argv', ['awswl', 'version']):
        main.main()

    assert 'awswl' in capsys.readouterr().out


def test_main_shows_help_when_no_args():
    """main() exits with SystemExit when invoked with no arguments (shows help)."""
    with patch('sys.argv', ['awswl']):
        with pytest.raises(SystemExit):
            main.main()


def test_execute_disable_current_with_add_current_prints_error(capsys):
    """execute() prints an error when --disable-current is used with add-current."""
    opt = Namespace()
    opt.command = 'add-current'
    opt.sgid = 'sg-12345'
    opt.sg_name = None
    opt.disable_current = True

    main.execute(opt)

    assert "Cannot use --disable-current with add-current" in capsys.readouterr().out


def test_execute_disable_current_with_remove_current_prints_error(capsys):
    """execute() prints an error when --disable-current is used with remove-current."""
    opt = Namespace()
    opt.command = 'remove-current'
    opt.sgid = 'sg-12345'
    opt.sg_name = None
    opt.disable_current = True

    main.execute(opt)

    assert "Cannot use --disable-current with remove-current" in capsys.readouterr().out


def test_execute_disable_current_with_update_current_prints_error(capsys):
    """execute() prints an error when --disable-current is used with update-current."""
    opt = Namespace()
    opt.command = 'update-current'
    opt.sgid = 'sg-12345'
    opt.sg_name = None
    opt.disable_current = True

    main.execute(opt)

    assert "Cannot use --disable-current with update-current" in capsys.readouterr().out
