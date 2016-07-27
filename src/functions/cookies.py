"""Various functions related to cookie loading and dumping"""
import json
import os
import requests.utils
import time

from .. import config


def dumpCookies(cookies):
    """Used to dump cookies from a session to a JSON file"""
    with open('cookies.json', 'w+') as f:
        cookieDict = {}
        for i in cookies:
            if not i.expires is None:
                cookieDict[i.name] = {}
                cookieDict[i.name]['value] = i.value
                cookieDict[i.name]['expires'] = i.expires
            else:
                pass

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
            c = json.load(f)
            d = {}
            for i in list(c.keys()):
                if c[i]['expires'] =< time.time():
                    pass
                else:
                    d[i] = c[i]['value']

            cookies = requests.utils.cookiejar_from_dict(d)
            return cookies
    else:
        getCookies(session)


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
