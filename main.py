###
# Copyright (c) 2015, wolfy1339
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
###

# Notice:
#   * This requires requests & BeutifulSoup4 from pypi,
#     sometimes it can be installed by default with your Python installation
#   * This code is fully PEP8 compliant,
#     and is Python 2 & 3 compatible (should be most of the time)
# Please respect point 2 of this notice when contributing.

from bs4 import BeautifulSoup
import config
from datetime import datetime
import os
import requests
import requests.utils
import json


class TPT(object):
    """A simple bot to automatically lock and delete old threads
    that haven't had any replies
    """
    # Variables used in the source
    def __init__(self):
        self.lockMsg = ''.join(config.tpt.lockmsg)
        self.referer = 'http://powdertoy.co.uk/Groups/Thread/View.html'
        self.referer += '?Group={0}'.format(config.tpt.groupID)
        self.white = self.mergeSort(config.tpt.whitelist)
        self.session = requests.Session()
        self.baseUrl = 'http://powdertoy.co.uk/Groups/'

        if not os.path.isfile('cookies.txt'):
            data = {
                'name': config.tpt.username,
                'pass': config.tpt.password,
                'Remember': 'Yes'
            }
            response = self.session.post(
                'https://powdertoy.co.uk/Login.html', data=data)
            with open('cookies.txt', 'w+') as f:
                cookies = self.session.cookies
                json.dump(requests.utils.dict_from_cookiejar(cookies, f))
        else:
            with open('cookies.txt') as f:
                cookies = requests.utils.cookiejar_from_dict(json.loads(f))
                self.session.cookies = cookies
                response = self.session.get('http://powdertoy.co.uk')
        response.raise_for_status()
        soup = BeautifulSoup(response.text).find('ul',
                                                 {'class': 'dropdown-menu'})
        li = soup.findAll('li', {'class': 'item'})[4]
        self.key = li.find('a')['href'].split('&Key=')[0]

    def whitelist(self, threadNum):
        """<thread number>

        Returns if a given thread is in the whitelist
        """
        return self.binarySearch(self.white, threadNum)

    def postRequest(self, url, data, headers=None, params=None, **kwargs):
        """<url> <headers> <POST data> [<URL parameters>]

        Wrapper function to do a POST request
        """
        req = self.session.request(
                'POST', url, headers=headers, data=data, allow_redirects=True,
                params=params, **kwargs)
        return req.raise_for_status()

    def threadModeration(self, action, threadNum, modKey):
        """<action> <thread number> <moderation key>

        Function to send the correct POST request to lock or delete a thread
        """
        # Example headers (includes server response headers):
        # http://hastebin.com/isugujeyeg.txt
        moderationURL = self.baseUrl + 'Thread/Moderation.html'
        if action.lower() == 'lock':
            data = {
                'Moderation_Lock': 'Lock'
            }
            ref = self.referer
            ref += '&Thread={0}'.format(threadNum)
        elif action.lower() == 'delete':
            data = {
                'Moderation_Delete': 'true',
                'Moderation_DeleteConfirm': 'Delete Thread'
            }
            ref = moderationURL
            ref += '?Group={0}&Thread={0}&Key={2}'.format(config.tpt.groupID,
                                                          threadNum, modKey)

        params = {
            'Group': config.tpt.groupID,
            'Thread': threadNum,
            'Key': modKey
        }
        headers = {
            'Referer': ref
        }
        self.postRequest(moderationURL, headers=headers, data=data,
                         params=params)

    def threadPost(self, message, threadNum, key):
        """<message> <thread number> <user key>

        Function to add a post to a thread
        """
        # Example headers (includes server response headers):
        # http://hastebin.com/epidazekah.txt
        ref = self.referer + '&Thread={0}'.format(threadNum)
        headers = {
            'Referer': ref
        }
        data = {
            'Thread': threadNum,
            'Post_Post': 'Post',
            'Post_Message': message
        }
        threadPostURL = 'http://powdertoy.co.uk/Groups/Thread/Reply.html'
        params = {
            'Group': config.tpt.groupID,
            'Key': key
        }
        self.postRequest(threadPostURL, headers=headers, data=data,
                         params=params)

    def timeToStr(self, date):
        """<date>

        Returns [day], [month], [year]
        """
        date = date.split(' ')
        date[0] = date[0].replace('th', '').replace('st', '').replace('rd', '').replace('nd', '')
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

        year = datetime.utcnow().year
        # If first half is day, so like 1 January
        if date[0].isdigit():
            return [str(date[0]), str(months.index(date[1]) + 1), str(year)]
        # Format like month - year
        elif len(date) == 2 and date[1].isdigit():
            return ['1', str(months.index(date[0]) + 1), str(date[1])]
        return [str(datetime.utcnow().day), '1', str(year)]

    def daysBetween(self, date):
        """<date>

        Calculate the difference in days between a given date
        and the current UTC date
        """
        dates = date[1] + ' ' + date[0] + ' ' + date[2] + '  1:00AM'
        d1 = datetime.strptime(dates, '%m %d %Y %I:%M%p')
        now = datetime.utcnow()
        nowDate = str(now.month) + ' ' + str(now.day) + ' ' + str(now.year)
        d2 = datetime.strptime(nowDate + '  1:00AM', '%m %d %Y %I:%M%p')
        return int(abs((d2 - d1).days))

    def cleanThreads(self):
        """No arguments

        Automated function to clean up threads that haven't received replies in
        a given time.
        """
        for i in list(range(10)):
            params = {
                'Group': config.tpt.groupID,
                'PageNum': i
            }
            groupURL = 'http://powdertoy.co.uk/Groups/Page/View.html'
            page = self.session.get(groupURL, params=params)
            page.raise_for_status()
            soup = BeautifulSoup(page.text, 'html5lib')

            # Get all links in ul.TopiList#TopicList
            # <ul id="TopicList" class="TopicList">

            threadData = []
            element = soup.find_all('a', {'class': 'Title'})
            icons = soup.find('ul', {'class': 'TopicList'}).find_all('img', {'class': 'TopicIcon'})
            length = list(range(len(element)))

            iconSrc = [icons[i]['src'] for i in length]
            titles = [i.text for i in element]
            threads = [element[i]["href"].split('&Thread=')[1] for i in length]
            dates = [i.text for i in soup.find_all('span', {'class': 'Date'})]
            key = self.key

            for i in length:
                data = [
                    threads[i],
                    titles[i],
                    dates[i],
                    iconSrc[i]
                ]
                threadData.append(data)

        for e in list(range(len(threadData))):
            threadNum = threadData[e][0]
            title = threadData[e][1]
            date = self.timeToStr(threadData[e][2])
            src = threadData[e][3]

            if not whitelist(threadNum) and src.find('Sticky') == -1:
                if daysBetween(date) >= 200:
                    self.threadBackup(threadNum)
                    threadModeration('delete', threadNum, key)
                elif daysBetween(date) >= 182:
                    # Lock thread if it isn't already
                    alert = soup.find('div',
                                      {'class': 'Warning'}) == -1
                    if alert:
                        threadPost(lockMsg, threadNum, key)
                        threadModeration('lock', threadNum, key)

    def saveBackUp(self, threadNum):
        """<thread num>

        Saves a copy of every thread page in seperate folders for each thread
        """
        # Save pages 0 through 1000
        for i in list(range(100)):
            url = self.baseUrl + 'Thread/View.html'
            url += '?Group={0}&Thread={1}'.format(config.tpt.groupId, threadNum)
            url += '&PageNum={1}'.fortmat(i)
            # Save the html to a folder under 'backups' named the threadNum
            newpath = r'Backups/' + str(threadNum)
            if not os.path.exists(newpath):
                os.makedirs(newpath)

            params = {
                'Group': config.tpt.groupId,
                'PageNum': i
            }

            # Get html from page replace links with saved copy
            groupURL = 'http://powdertoy.co.uk/Groups/Page/View.html'
            page = self.session.get(url)
            page.raise_for_status()
            if page.text.find('<div id="MessageContainer"') == -1:
                break
            path = 'Backups/' + threadNum + '/' + 'backup-' + str(i) + '.html'
            open(path, 'w+').write(page.text)

    def mergeSort(alist):
        # Ahh the internet where you can steal code for any algorithim
        if len(alist) > 1:
            mid = len(alist)//2
            lefthalf = alist[:mid]
            righthalf = alist[mid:]

            mergeSort(lefthalf)
            mergeSort(righthalf)

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
        # Modified binary search
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

a = TPT()
a.cleanThreads()

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
