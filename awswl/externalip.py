import requests


def get_external_ip():
    return requests.get('https://checkip.amazonaws.com').text.rstrip()
