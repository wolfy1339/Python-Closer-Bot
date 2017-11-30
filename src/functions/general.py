"""General functions required"""
import os
import json
from bs4 import BeautifulSoup
from . import cookies


def loadDataFile():
    """No arguments

    Loads the JSON data file and does the correct data transformations
    if needed
    """
    if not os.path.isfile('thread.json'):
        threadData = self.getThreadData()
    else:
        with open('thread.json') as t:
            threadData = json.load(t)

        if isinstance(threadData, list):
            raise TypeError('WARNING: Invalid data type!')
    return threadData


def getKey(session):
    """Used to get the user key in order to post, and do moderation tasks"""
    response = session.get('/Groups/Page/Groups.html')
    if response.status_code in (401, 403):
        cookies.getCookies(session)
    arg = {
        'class': 'dropdown-menu'
    }
    soup = BeautifulSoup(response.text, 'html5lib').find('ul', arg)
    li = soup.findAll('li', {'class': 'item'})[4]
    return li.find('a')['href'].split('?Key=')[1]


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
