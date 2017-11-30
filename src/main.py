"""
Main file containing all the logic needed
in order to run the automated thread closer bot
"""
from __future__ import print_function

import json
import os
import requests
from requests_toolbelt import sessions
from bs4 import BeautifulSoup as bs

from . import config
from .confirm import confirm
from .functions.date import Dates
from .functions.whitelist import Whitelist

# Notice:
#   * This requires requests & BeutifulSoup4 from pypi,
#     sometimes they might be included by default with your Python installation
#   * This code is fully PEP8 compliant,
#     and is Python 2 & 3 compatible (should be most of the time)
# Please respect point 2 of this notice when contributing.


class TPT(Dates, Whitelist):
    """
    A simple bot to automatically lock and delete old threads
    that haven't had any replies
    """
    # Variables used in the source
    def __init__(self, lockmsg=config.tpt.lockmsg, groupId=config.tpt.groupID,
                 daysUntilLock=config.tpt.daysUntilLock,
                 daysUntilDelete=config.tpt.daysUntilDelete):
        super(TPT, self).__init__()
        self.lockMsg = lockmsg
        self.referer = 'http://powdertoy.co.uk/Groups/Thread/View.html'
        self.referer += '?Group={0}'.format(groupId)
        self.session = sessions.BaseUrlSession(base_url="http://powdertoy.co.uk")
        self.session.cookies = functions.cookies.loadCookies(self.session)
        self.baseUrl = '/Groups/'
        self.key = functions.general.getKey(self.session)
        self.groupID = groupId
        self.daysUntilLock = daysUntilLock
        self.daysUntilDelete = daysUntilDelete
        self.loadDataFile = functions.general.loadDataFile

    def _post(self, url, data, headers=None, params=None, **kwargs):
        """<url> <headers> <POST data> [<URL parameters>]

        Wrapper function to do a POST request
        """
        req = self.session.request(
            'POST', url, headers=headers, data=data, allow_redirects=True,
            params=params, **kwargs)
        return req.raise_for_status()

    def threadModeration(self, action, threadNum, modKey):
        """<action> <thread number> <moderation key>

        Function to send the correct POST request in order to
        either lock or delete a thread
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
            ref += '?Group={0}&Thread={1}&Key={2}'.format(self.groupID,
                                                          threadNum, modKey)

        params = {
            'Group': self.groupID,
            'Thread': threadNum,
            'Key': modKey
        }
        headers = {
            'Referer': ref
        }
        self._post(moderationURL, headers=headers, data=data,
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
        threadPostURL = self.baseUrl + 'Thread/Reply.html'
        params = {
            'Group': self.groupID,
            'Key': key
        }
        self._post(threadPostURL, headers=headers, data=data,
                   params=params)

    def getThreadData(self):
        """No arguments

        Gathers data about the threads in the Group
        """
        params = {
            'Group': self.groupID,
        }
        page = self.session.get(self.baseUrl + 'Page/View.html',
                                 params=params)
        # Get number of pages of threads
        p = bs(page.text, "html5lib").find("div", {'class': 'Pageheader'}).find_all("li")[-2].string
        for i in list(range(int(p))):
            params['PageNum'] = str(i)
            page = self.session.get(self.baseUrl + 'Page/View.html',
                                    params=params)
            page.raise_for_status()
            soup = bs(page.text, 'html5lib')
            threadData = {}

            # Get all links in ul.TopiList#TopicList
            # <ul id="TopicList" class="TopicList">
            element = soup.find_all('a', {'class': 'Title'})

            icons = soup.find_all('img', {'class': 'TopicIcon'})
            length = list(range(len(element)))

            iconSrc = [icons[i]['src'] for i in length]
            titles = [i.text for i in element]
            threads = [element[i]['href'].split('&Thread=')[1] for i in length]
            dates = soup.find_all('span', {'class': 'Date'})

            for n in length:
                threadNum = threads[n]
                del params['PageNum']
                params['Thread'] = threadNum
                res = self.session.get(self.base_url + 'Thread/View.html', params=params)
                res.raise_for_status()
                soup = bs(res.text, 'html5lib')
                pages = soup.find('div', {'class': 'pagination'}).find_all('li')[-2].string
                threadData[threadNum] = [
                    titles[n],
                    self.timeToArray(dates[n].text),
                    iconSrc[n].find('Sticky') != -1,
                    int(pages)
                ]
        with open('thread.json', 'w+') as t:
            json.dump(threadData, t, indent=2, separators=(',', ': '))
        return threadData

    def cleanThreads(self, delete=True, doConfirm=False):
        """No arguments

        Automated function to clean up threads that haven't received replies in
        a given time.
        """
        threadData = self.loadDataFile()
        for e in threadData:
            threadNum = e
            title = threadData[e][0]
            date = threadData[e][1]
            sticky = threadData[e][2] # Check whether this thread is stickied

            params = {
                'Group': self.groupID,
                'Thread': threadNum
            }
            groupURL = self.baseUrl + 'Thread/View.html'
            page = self.session.get(groupURL, params=params)
            page.raise_for_status()
            soup = bs(page.text, 'html5lib')
            locked = soup.find('div',
                                {'class': 'Warning'}) != -1
            msg = 'Would you like to delete thread {0} {1}?'.format(threadNum,
                                                                    title)
            if not self.whitelist(threadNum) and not sticky:
                if (self.daysBetween(date) >= self.daysUntilDelete and
                        locked and delete):
                    self.threadBackup(threadNum)
                    if doConfirm:
                        if confirm(msg):
                            self.threadModeration('delete',
                                                  threadNum, self.key)
                            print('Deleted thread {0} {1}'.format(threadNum,
                                                                  title))
                        else:
                            pass
                    else:
                        self.threadModeration('delete', threadNum, self.key)
                        print('Deleted thread {0} {1}'.format(threadNum,
                                                              title))
                elif self.daysBetween(date) >= self.daysUntilLock:
                    # Lock thread if it isn't already
                    if not locked:
                        self.threadPost(self.lockMsg, threadNum, self.key)
                        self.threadModeration('lock', threadNum, self.key)

    def threadBackup(self, threadNum):
        """<thread num>

        Saves a copy of every thread page in seperate folders for each thread
        """
        # Save pages 0 through 1000
        threadData = self.loadDataFile()
        for e in threadData:
            url = self.baseUrl + 'Thread/View.html'
            # Save the html to a folder under 'backups' named the threadNum
            threadNum = threadData[e][0]
            newpath = r'Backups/' + str(threadNum)
            if not os.path.exists(newpath):
                os.makedirs(newpath)

            params = {
                'Group': self.groupID,
                'Thread': threadNum
            }

            page = self.session.get(url, params=params)
            page.raise_for_status()
            if page.text.find('<div id="MessageContainer"') == -1:
                break
            # Get page count
            pages = threadData[3]
            
            for i in range(pages):
                # Don't fetch the first page for nothing
                if i > 1:
                    params["PageNum"] = i
                    page = self.session.get(url, params=params)
                path = 'Backups/' + threadNum + '/' + 'page-' + str(i) + '.html'
                with open(path, 'w+') as w:
                    w.write(page.text)


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
