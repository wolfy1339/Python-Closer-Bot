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
#   * This requires requests & BeutifulSoup4 from pypi
#   * This code is fully PEP8 compliant,
#     and is Python 2 & 3 compatible (should be most of the time)
# Please respect point 2 of this notice when contributing.

from bs4 import BeautifulSoup
from config import tpt
from datetime import datetime
import os
import pickle
import requests
import requests.utils


class TPT(object):
    """A simple bot to automatically lock and delete old threads
    that haven't had any replies
    """
    # Variables used in the source
    lockMsg = ''.join(tpt['lockmsg'])
    referer = 'http://powdertoy.co.uk/Groups/Thread/View.html'
    referer += '?Group=832'
    white = tpt['whitelist']
    session = requests.Session()


    if not os.path.isfile('cookies'):
        data = {
            'name': tpt['username'],
            'pass': tpt['password'],
            'Remember': 'Yes'
        }
        response = session.request(
            'POST', 'https://powdertoy.co.uk/Login.html', data=data)
        response.raise_for_status()
        with open('cookies', 'w+') as f:
            pickle.dump(
                requests.utils.dict_from_cookiejar(session.cookies), f)
    else:
        with open('cookies') as f:
            cookies = requests.utils.cookiejar_from_dict(pickle.load(f))
            session.cookies.set(list(cookies.keys())[0],
                                list(cookies.values())[0])

    def whitelist(self, threadNum):
        """<thread number>

        Returns if a given thread is in the whitelist"""
        for a in self.white:
            if threadNum == a:
                return True
        return False

    def postRequest(self, url, data, headers=None, params=None, **kwargs):
        """<url> <headers> <POST data> [<URL parameters>]

        Wrapper function to do a POST request"""
        req = self.session.request(
                'POST', url, headers=headers, data=data, allow_redirects=True,
                params=params, **kwargs)
        return req.raise_for_status()

    def threadModeration(self, type, threadNum, modKey):
        """<type> <thread number> <moderation key>

        Function to send the correct POST request to lock or delete a thread"""
        # Example headers (includes server response headers):
        # http://hastebin.com/isugujeyeg.txt
        moderationURL = 'http://powdertoy.co.uk/Groups/Thread/Moderation.html'
        if type.lower() == 'lock':
            data = {
                'Moderation_Lock': 'Lock'
            }
            ref = self.referer
            ref += '&Thread={0}'.format(threadNum)
        elif type.lower() == 'delete':
            data = {
                'Moderation_Delete': 'true',
                'Moderation_DeleteConfirm': 'Delete Thread'
            }
            ref = moderationURL
            ref += '?Group=832&Thread={0}&Key={1}'.format(threadNum, modKey)

        params = {
            'Group': '832',
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

        Function to add a post to a thread"""
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
            'Group': '832',
            'Key': key
        }
        self.postRequest(threadPostURL, headers=headers, data=data,
                         params=params)

    def timestr_to_obj(datetime_str):
        """<date>

        Converts a date string to a datetime.datetime object"""
        # Current date and time in UTC
        datetime_now = datetime.utcnow()
        # Current date in "Day Month" format
        current_date = datetime_now.strftime("%d %B")
        # Current year
        current_year = datetime_now.strftime("%Y")

        # Check if the datetime string is in the format "Hour:Minute:Year"
        if ":" in datetime_str:
            # Convert it to "Hour:Minute:year Day Month Year"
            datetime_str = "{0} {1} {2}".format(
                datetime_str, current_date, current_year)

        # Check if the datetime string is in the format
        # "Day(st|nd|rd|th) Month"
        elif datetime_str[0].isdigit():
            # Remove the ordinal indicator
            datetime_str = re.sub(r"^(\d+)(st|nd|rd|th)", r"\1", datetime_str)
            # The day must be a zero-padded decimal number
            if datetime_str[1] == " ":
                datetime_str = "0" + datetime_str
                # Convert it to "Hour:Minute:year Day Month Year"
                datetime_str = "00:00:00 {0} {1}".format(
                    datetime_str, current_year)

                # Check if the datetime string is in the format "Month Year"
            else:
                # Convert it to "Hour:Minute:year Day Month Year"
                datetime_str = "00:00:00 1 " + datetime_str

            # Convert the datetime string to a datetime.datetime object
            datetime_obj = datetime.strptime(
                datetime_str, "%H:%M:%S %d %B %Y")

        return datetime_obj

    def days_between(date):
        """<date>

        Calculate the difference in days between a given date
        and the current UTC date"""
        d1 = datetime.strptime(str(date, '%Y-%m-%d'))
        d2 = datetime.strptime(str(datetime.utcnow()), '%Y-%m-%d')
        return abs((d2 - d1).days)

    for i in list(range(0, 10)):
        params = {
            'Group': '832',
            'PageNum': i
        }
        groupURL = 'http://powdertoy.co.uk/Groups/Page/View.html'
        page = session.get(groupURL, params=params)
        page.raise_for_status()
        soup = BeautifulSoup(page.text, 'html5lib')

        # Get all links in ul.TopiList#TopicList
        # <ul id="TopicList" class="TopicList">

        threadData = []
        title = [i.text for i in soup.find_all('a', {'class': 'Title'})]
        threads = [title[i]["href"].split('&Thread=')[1] for i in list(range(len(title)))]
        dates = [i.text for i in soup.find_all('span', {'class': 'Date'})]
        # Fetch key from page since the key seems to change sometimes
        key = soup.find('form', {'class': 'PostFForm'})['action'].split(
            '&Key=')[1]

        for i in list(range(len(dates))):
            threadData.append([threads[i], title[i], dates[i]])

        for e in list(range(len(threadData))):
            threadNum = threadData[e][0]
            title = threadData[e][1]
            date = timestr_to_obj(threadData[e][2])

            if not whitelist(threadNum):
                if days_between(date) >= 182:
                    # Lock thread if it isn't already
                    alert = soup.find('div',
                                      {'class': 'Warning'})
                    if alert == -1:
                        threadPost(lockMsg, threadNum, key)
                        threadModeration('lock', threadNum, key)
                elif days_between(date) >= 200:
                    threadModeration('delete', threadNum, key)

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
