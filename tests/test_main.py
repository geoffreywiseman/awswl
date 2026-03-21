from unittest.mock import patch

import pytest

from awswl import main


def test_unexpected_command(options, capsys):
    main.execute(options(command="fubar", sgid="sg-12345"))

    assert capsys.readouterr().out == "Unexpected command: fubar\n"


def test_execute_requires_security_group(options, capsys):
    """execute() prints an error and returns when no security group is specified."""
    main.execute(options(command='list'))

    assert "You must specify a security group" in capsys.readouterr().out


def test_execute_version_skips_sg_check(options, capsys):
    """The 'version' command bypasses the security-group requirement."""
    main.execute(options(command='version'))

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


def test_execute_disable_current_with_add_current_prints_error(options, capsys):
    """execute() prints an error when --disable-current is used with add-current."""
    main.execute(options(command='add-current', sgid='sg-12345', disable_current=True))

    assert "Cannot use --disable-current with add-current" in capsys.readouterr().out


def test_execute_disable_current_with_remove_current_prints_error(options, capsys):
    """execute() prints an error when --disable-current is used with remove-current."""
    main.execute(options(command='remove-current', sgid='sg-12345', disable_current=True))

    assert "Cannot use --disable-current with remove-current" in capsys.readouterr().out


def test_execute_disable_current_with_update_current_prints_error(options, capsys):
    """execute() prints an error when --disable-current is used with update-current."""
    main.execute(options(command='update-current', sgid='sg-12345', disable_current=True))

    assert "Cannot use --disable-current with update-current" in capsys.readouterr().out
