"""
Main file containing all the logic needed
in order to run the automated thread closer bot
"""
from __future__ import print_function

from bs4 import BeautifulSoup
import json
import os
import requests
import requests.utils

from . import config
from confirm import confirm as confirmed
import functions

# Notice:
#   * This requires requests & BeutifulSoup4 from pypi,
#     sometimes they might be included by default with your Python installation
#   * This code is fully PEP8 compliant,
#     and is Python 2 & 3 compatible (should be most of the time)
# Please respect point 2 of this notice when contributing.


class TPT(object):
    """
    A simple bot to automatically lock and delete old threads
    that haven't had any replies
    """
    # Variables used in the source
    def __init__(self):
        self.lockMsg = ''.join(config.tpt.lockmsg)
        self.referer = 'http://powdertoy.co.uk/Groups/Thread/View.html'
        self.referer += '?Group={0}'.format(config.tpt.groupID)
        self.session = requests.Session()
        self.session.cookies = functions.loadCookies(self.session)
        self.baseUrl = 'http://powdertoy.co.uk/Groups/'
        dates = functions.dates()
        whitelistClass = functions.whitelist()
        self.timeToArray = dates.timeToArray
        self.daysBetween = dates.daysBetween
        self.whitelist = whitelistClass.isWhitelisted
        self.key = functions.getKey(self.session)

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
            ref += '?Group={0}&Thread={1}&Key={2}'.format(config.tpt.groupID,
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
        threadPostURL = self.baseUrl + 'Thread/Reply.html'
        params = {
            'Group': config.tpt.groupID,
            'Key': key
        }
        self.postRequest(threadPostURL, headers=headers, data=data,
                         params=params)

    def getThreadData(self):
        """No arguments

        Gathers data about the threads in the Group
        """
        for i in list(range(10)):
            params = {
                'Group': config.tpt.groupID,
                'PageNum': str(i)
            }
            page = self.session.get(self.baseUrl + 'Page/View.html',
                                    params=params)
            page.raise_for_status()
            soup = BeautifulSoup(page.text, 'html5lib')
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
            dateArray = [self.timeToArray(i.text) for i in dates]

            for i in length:
                threadData[threads[i]] = [
                    titles[i],
                    dateArray[i],
                    iconSrc[i]
                ]
        with open('thread.json', 'w+') as t:
            json.dump(threadData, t, indent=2, separators=(',', ': '))
        return threadData

    def loadDataFile(self):
        """No arguments

        Loads the JSON data file and does the correct data transformations
        if needed
        """
        if not os.path.isfile('thread.json'):
            threadData = self.getThreadData()
        else:
            with open('thread.json') as t:
                tData = json.loads(t)

            if type(threadData) is 'list':
                print('WARNING: Invalid data type!')
                threadData = {}
                for i in list(range(len(tData))):
                    data = [
                        tData[i][1],
                        tData[i][2],
                        tData[i][3]
                    ]
                    threadData[tData[i][0]] = data
                with open('thread.json', 'w+') as t:
                    json.dump(threadData, t, indent=2, separators=(',', ': '))
        return threadData

    def cleanThreads(self, delete=True, confirm=False):
        """No arguments

        Automated function to clean up threads that haven't received replies in
        a given time.
        """
        threadData = self.loadDataFile()
        for e in list(threadData.keys()):
            threadNum = threadData[e][0]
            title = threadData[e][1]
            date = threadData[e][2]
            src = threadData[e][3]
            sticky = src.find('Sticky') != -1

            params = {
                'Group': config.tpt.groupID,
                'Thread': threadNum
            }
            groupURL = self.baseUrl + 'Thread/View.html'
            page = self.session.get(groupURL, params=params)
            page.raise_for_status()
            soup = BeautifulSoup(page.text, 'html5lib')
            alert = soup.find('div',
                              {'class': 'Warning'}) != -1
            msg = 'Would you like to delete thread {0} {1}?'.format(threadNum,
                                                                    title)
            if not self.whitelist(threadNum) and not sticky:
                if self.daysBetween(date) >= 200 and alert and delete:
                    self.threadBackup(threadNum)
                    if confirm:
                        if confirmed(msg):
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
                elif self.daysBetween(date) >= 182:
                    # Lock thread if it isn't already
                    if not alert:
                        self.threadPost(self.lockMsg, threadNum, self.key)
                        self.threadModeration('lock', threadNum, self.key)

    def threadBackup(self, threadNum):
        """<thread num>

        Saves a copy of every thread page in seperate folders for each thread
        """
        # Save pages 0 through 1000
        for i in list(range(100)):
            url = self.baseUrl + 'Thread/View.html'
            # Save the html to a folder under 'backups' named the threadNum
            newpath = r'Backups/' + str(threadNum)
            if not os.path.exists(newpath):
                os.makedirs(newpath)

            params = {
                'Group': config.tpt.groupId,
                'Thread': threadNum,
                'PageNum': i
            }

            # Get html from page replace links with saved copy
            page = self.session.get(url, params=params)
            page.raise_for_status()
            if page.text.find('<div id="MessageContainer"') == -1:
                break
            path = 'Backups/' + threadNum + '/' + 'page-' + str(i) + '.html'
            with open(path, 'w+') as w:
                w.write(page.text)


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
