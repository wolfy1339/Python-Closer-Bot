"""
Various helper functions
"""
from bs4 import BeautifulSoup
import json
import os
import requests.utils
from datetime import datetime
import config

def dumpCookies(cookies):
    """Used to dump cookies from a session to a JSON file"""
    with open('cookies.txt', 'w+') as f:
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


def getKey(session):
    """Used to get the user key in order to post, and do moderation tasks"""
    response = session.get('http://powdertoy.co.uk')
    arg = {
        'class': 'dropdown-menu'
    }
    soup = BeautifulSoup(response.text, 'html5lib').find('ul', arg)
    li = soup.findAll('li', {'class': 'item'})[4]
    return li.find('a')['href'].split('?Key=')[1]

class dates(object):
    """Contains several date functions"""
    def timeToArray(self, string):
        """<date>

        Returns [day], [month], [year] array
        """
        data = string.split(' ')[0].replace('th', '').replace('st', '')
        date = data.replace('rd', '').replace('nd', '')
        months = [
            'January',
            'February',
            'March',
            'April',
            'May',
            'June',
            'July',
            'Augu',
            'September',
            'October',
            'November',
            'December',
        ]
        now = datetime.utcnow()
        # In h:min:second format
        if string.find(":") == 2:
            return [str(now.day), str(now.month), str(now.year)]

        year = datetime.utcnow().year
        # If first half is day, so like 1 January
        if date.isdigit():
            return [str(date), str(months.index(data[1]) + 1), str(year)]
        # Format like month - year
        elif len(date) == 2 and data[1].isdigit():
            return ['1', str(months.index(date) + 1), str(data[1])]
        return [str(now.day), '1', str(year)]

    def daysBetween(date):
        """<date>

        Calculate the difference in days between a given date
        and the current UTC date
        """
        dateFormatted = date[1] + ' ' + date[0] + ' ' + date[2] + '  1:00AM'
        d1 = datetime.strptime(dateFormatted, '%m %d %Y %I:%M%p')
        now = datetime.utcnow()
        nowDate = str(now.month) + ' ' + str(now.day) + ' ' + str(now.year)
        d2 = datetime.strptime(nowDate + '  1:00AM', '%m %d %Y %I:%M%p')
        return int(abs((d2 - d1).days))

class whitelist(object):
    """Contains functions related to the whitelist"""
    def __init__(self):
        self.white = self.mergeSort(config.tpt.whitelist)

    def mergeSort(self, alist):
        """<list>

        Sort's a list to be used with self.binarySearch
        """
        # Ahh the internet where you can steal code for any algorithim
        if len(alist) > 1:
            mid = len(alist)//2
            lefthalf = alist[:mid]
            righthalf = alist[mid:]

            self.mergeSort(lefthalf)
            self.mergeSort(righthalf)

            i = 0
            j = 0
            k = 0

            while i < len(lefthalf) and j < len(righthalf):
                if int(lefthalf[i]) < int(righthalf[j]):
                    alist[k] = lefthalf[i]
                    i = i + 1
                else:
                    alist[k] = righthalf[j]
                    j = j + 1
                k = k + 1

            while i < len(lefthalf):
                alist[k] = lefthalf[i]
                i = i + 1
                k = k + 1

            while j < len(righthalf):
                alist[k] = righthalf[j]
                j = j + 1
                k = k + 1
        return alist

    def binarySearch(sequence, value):
        """<sequence> <value>

        Modified binary search
        """
        lo, hi = 0, len(sequence) - 1
        while lo <= hi:
            mid = (lo + hi) / 2

            if int(sequence[mid]) < int(value):
                lo = mid + 1
            elif int(value) < int(sequence[mid]):
                hi = mid - 1
            elif int(value) == int(sequence[mid]):
                return sequence[mid]
            else:
                return True
        return False

    def isWhitelisted(self, threadNum):
        """<thread number>

        Returns if a given thread is in the whitelist
        """
        return self.binarySearch(self.white, threadNum)

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
