"""
dlsitelib
=========

Shared library for dlsite functions.

"""

import urllib.request
import re

from bs4 import BeautifulSoup

_DLSITE_URL = 'http://www.dlsite.com/maniax/work/=/product_id/{}.html'


class RJCode:

    _RJCODE_PATTERN = re.compile(r'(RJ[0-9]+)')

    def __init__(self, rjcode):
        self.rjcode = rjcode

    @classmethod
    def from_string(cls, string):
        """Get RJ code from a string."""
        match = cls._RJCODE_PATTERN.search(string)
        if match:
            rjcode = cls._RJCODE_PATTERN.search(string).group(1)
            return cls(rjcode)
        else:
            raise ValueError('No rjcode found.')

    def __str__(self):
        return self.rjcode

    @property
    def url(self):
        return _DLSITE_URL.format(self.rjcode)


class WorkInfo:

    def __init__(self, rjcode, name, maker):
        self.rjcode = rjcode
        self.name = name
        self.maker = maker

    @classmethod
    def from_rjcode(cls, rjcode):
        data = urllib.request.urlopen(rjcode.url).read()
        soup = BeautifulSoup(data.decode(), 'lxml')
        work_name = soup.find(id="work_name").a.contents[-1]
        maker_name = soup.find(id="work_maker")
        maker_name = maker_name.find(**{'class': 'maker_name'}).a.string
        return cls(rjcode, work_name, maker_name)

    def __str__(self):
        return '{} [{}] {}'.format(self.rjcode, self.maker, self.name)
