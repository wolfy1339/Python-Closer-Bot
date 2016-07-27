"""Various functions related to cookie loading and dumping"""
import json
import os
import requests.utils

from .. import config


def dumpCookies(cookies):
    """Used to dump cookies from a session to a JSON file"""
    with open('cookies.json', 'w+') as f:
        cookieDict = requests.utils.dict_from_cookiejar(cookies)
        json.dump(cookieDict, f, indent=2, separators=(',', ': '))


def getCookies(session):
    """Used to login into The Powder Toy's website"""
    data = {
        'name': config.tpt.username,
        'pass': config.tpt.password,
        'Remember': 'Yes'
    }
    session.post(
        'https://powdertoy.co.uk/Login.html', data=data)
    dumpCookies(session.cookies)
    return session.cookies

def loadCookies(session):
    """Used to return cookies loaded from a JSON file"""
    if os.path.isfile('cookies.json'):
        with open('cookies.json') as f:
            cookies = requests.utils.cookiejar_from_dict(json.load(f))
            return cookies
    else:
        getCookies(session)


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
