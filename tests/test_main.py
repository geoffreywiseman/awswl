from unittest.mock import patch

import pytest

from awswl import main


def test_unexpected_command(bare_options, capsys):
    bare_options.command = "fubar"
    bare_options.sgid = "sg-12345"

    main.execute(bare_options)

    assert capsys.readouterr().out == "Unexpected command: fubar\n"


def test_execute_requires_security_group(bare_options, capsys):
    """execute() prints an error and returns when no security group is specified."""
    bare_options.command = 'list'

    main.execute(bare_options)

    assert "You must specify a security group" in capsys.readouterr().out


def test_execute_version_skips_sg_check(bare_options, capsys):
    """The 'version' command bypasses the security-group requirement."""
    bare_options.command = 'version'

    main.execute(bare_options)

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


def test_execute_disable_current_with_add_current_prints_error(bare_options, capsys):
    """execute() prints an error when --disable-current is used with add-current."""
    bare_options.command = 'add-current'
    bare_options.sgid = 'sg-12345'
    bare_options.disable_current = True

    main.execute(bare_options)

    assert "Cannot use --disable-current with add-current" in capsys.readouterr().out


def test_execute_disable_current_with_remove_current_prints_error(bare_options, capsys):
    """execute() prints an error when --disable-current is used with remove-current."""
    bare_options.command = 'remove-current'
    bare_options.sgid = 'sg-12345'
    bare_options.disable_current = True

    main.execute(bare_options)

    assert "Cannot use --disable-current with remove-current" in capsys.readouterr().out


def test_execute_disable_current_with_update_current_prints_error(bare_options, capsys):
    """execute() prints an error when --disable-current is used with update-current."""
    bare_options.command = 'update-current'
    bare_options.sgid = 'sg-12345'
    bare_options.disable_current = True

    main.execute(bare_options)

    assert "Cannot use --disable-current with update-current" in capsys.readouterr().out
