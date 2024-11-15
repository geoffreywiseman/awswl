import io
from argparse import Namespace
from unittest.mock import patch

from awswl import main

@patch('sys.stdout', new_callable=io.StringIO)
def test_unexpected_command(mock_stdout):
    # Given
    opt = Namespace()
    opt.command = "fubar"
    opt.sgid = "sg-12345"
    opt.sg_name = None

    # When
    main.execute(opt)

    # Then
    assert mock_stdout.getvalue() == "Unexpected command: fubar\n"
