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

from collections import namedtuple
import urllib.request
import re

from bs4 import BeautifulSoup

__version__ = '0.1.0'

_RJCODE_PATTERN = re.compile(r'RJ[0-9]+')


def parse_rjcodes(string) -> 'Iterable':
    """Parse all RJ codes from a string."""
    for match in _RJCODE_PATTERN.finditer(string):
        yield match.group(0)


def parse_rjcode(string) -> str:
    """Parse RJ code from a string."""
    try:
        return next(parse_rjcodes(string))
    except StopIteration:
        raise ValueError('No rjcode found.')


class WorkInfoFetcher:

    _DLSITE_URL = 'http://www.dlsite.com/maniax/work/=/product_id/{}.html'

    def __call__(self, rjcode: str) -> 'WorkInfo':
        page = self._get_page(rjcode)
        soup = BeautifulSoup(page, 'lxml')
        return WorkInfo(
            rjcode=rjcode,
            name=self._get_name(soup),
            maker=self._get_maker(soup),
            series=self._get_series(soup))

    def _get_name(self, soup) -> str:
        """Get the work name."""
        return soup.find(id="work_name").a.contents[-1].strip()

    def _get_maker(self, soup) -> str:
        """Get the work maker."""
        return (soup.find(id="work_maker")
                .find(**{'class': 'maker_name'})
                .a.string)

    _series_pattern = re.compile('^シリーズ名')

    def _get_series(self, soup) -> str:
        """Get work series name."""
        try:
            return (soup.find(id='work_outline')
                    .find('th', string=self._series_pattern)
                    .find_next_sibling('td')
                    .a.string)
        except AttributeError:
            return ''

    def _get_page(self, rjcode: str) -> str:
        """Get webpage text for a work."""
        url = self._get_url(rjcode)
        return urllib.request.urlopen(url).read().decode()

    def _get_url(self, rjcode: str) -> str:
        """Get DLSite URL corresponding to an RJ code."""
        return self._DLSITE_URL.format(rjcode)


class WorkInfo(namedtuple('WorkInfo', 'rjcode,name,maker,series')):

    def __new__(cls, rjcode, name, maker, series=''):
        return super().__new__(cls, rjcode, name, maker, series)

    def __str__(self):
        return '{} [{}] {}'.format(self.rjcode, self.maker, self.name)
