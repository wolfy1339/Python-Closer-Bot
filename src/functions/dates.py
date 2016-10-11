"""Several functions pertaining to date manipulation and comparision"""
from datetime import datetime, date


class Dates(object):
    """Contains several date functions"""
    def timeToArray(self, string):
        """<date>

        Returns [day], [month], [year] array
        """
        data = string.split(' ')
        data[0] = data[0].replace('th', '').replace('st', '')
        date = data[0].replace('rd', '').replace('nd', '')
        months = [
            'January',
            'February',
            'March',
            'April',
            'May',
            'June',
            'July',
            'August',
            'September',
            'October',
            'November',
            'December',
        ]
        now = datetime.utcnow()
        # In h:min:second format
        if string.find(":") == 2:
            return [str(now.day), str(now.month), str(now.year)]

        year = now.year
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
        dateFormatted = date[1] + ' ' + date[0] + ' ' + date[2]
        d1 = date.strftime(dateFormatted, '%m %d %Y')
        now = datetime.utcnow()
        nowDate = str(now.month) + ' ' + str(now.day) + ' ' + str(now.year)
        d2 = date.strftime(nowDate, '%m %d %Y')
        return int(abs((d2 - d1).days))


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
