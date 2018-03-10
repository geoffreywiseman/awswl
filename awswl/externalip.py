import requests


def get_external_ip():
    return requests.get('https://api.ipify.org').text
