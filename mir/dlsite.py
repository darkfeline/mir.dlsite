# Copyright (C) 2016 Allen Li
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""dlsite library"""

import collections
import urllib.request
import re

from bs4 import BeautifulSoup


class RJCode(str):

    __slots__ = ()
    _RJCODE_PATTERN = re.compile(r'(RJ[0-9]+)')
    _DLSITE_URL = 'http://www.dlsite.com/maniax/work/=/product_id/{}'

    def __new__(cls, obj):
        if not isinstance(obj, str):
            raise TypeError('RJCode constructor argument must be a string')
        match = cls._RJCODE_PATTERN.match(obj)
        if match is None or match.end() < len(obj):
            raise ValueError('%r is not a valid RJCode' % obj)
        return super().__new__(cls, obj)

    @classmethod
    def from_string(cls, string):
        """Get RJ code from a string."""
        match = cls._RJCODE_PATTERN.search(string)
        if match:
            rjcode = cls._RJCODE_PATTERN.search(string).group(1)
            return cls(rjcode)
        else:
            raise ValueError('No rjcode found.')

    @property
    def url(self):
        return self._DLSITE_URL.format(self)


class WorkInfo:

    def __init__(self, rjcode, name, maker):
        self.rjcode = rjcode
        self.name = name
        self.maker = maker

    @classmethod
    def from_rjcode(cls, rjcode):
        data = urllib.request.urlopen(rjcode.url).read()
        soup = BeautifulSoup(data.decode(), 'lxml')
        work_name = soup.find(id="work_name").a.contents[-1].strip()
        work_maker = soup.find(id="work_maker")
        maker_name = work_maker.find(**{'class': 'maker_name'}).a.string
        return cls(rjcode, work_name, maker_name)

    def __str__(self):
        return '{} [{}] {}'.format(self.rjcode, self.maker, self.name)
