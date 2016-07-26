from .. import config

class Whitelist(object):
    """Contains functions related to the whitelist"""
    def __init__(self, white=config.tpt.whitelist):
        self.white = self.mergeSort(white)

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

    def isWhitelisted(self, threadNum):
        """<thread number>

        Returns if a given thread is in the whitelist
        """
        return self.binarySearch(self.white, threadNum)


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
