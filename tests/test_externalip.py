from awswl import externalip
from argparse import Namespace

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


@patch('requests.get')
def test_get_externalip(get_method):
    # Given
    example_ip = '192.0.2.1'
    response = Namespace()
    response.text = example_ip
    get_method.return_value = response

    # When
    external_ip = externalip.get_external_ip()

    # Then
    assert external_ip == example_ip
