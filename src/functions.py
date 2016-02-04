###
# Copyright (c) 2015-2016, wolfy1339 and contributors
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

from datetime import datetime

class dates:
    """Contains several date functions"""
    def timeToArray(self, string):
        """<date>

        Returns [day], [month], [year] array
        """
        data = string.split(' ')
        date = data[0].replace('th', '').replace('st', '').replace('rd', '').replace('nd', '')
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

class whitelist:
    """Contains functions related to the whitelist"""
    def mergeSort(self, alist):
        """<list>

        Sort's a list to be used with self.binarySearch
        """
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

    def binarySearch(self, sequence, value):
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

    def whitelist(self, threadNum):
        """<thread number>

        Returns if a given thread is in the whitelist
        """
        return self.binarySearch(self.white, threadNum)

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
