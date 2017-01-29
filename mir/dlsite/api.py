# Copyright (C) 2016, 2017 Allen Li
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

"""DLsite API"""

import os
import pathlib
import re
import shelve
import urllib.request

from bs4 import BeautifulSoup


class WorkInfoFetcher:

    """Fetches DLsite work information."""

    _ROOT = 'http://www.dlsite.com/maniax/'
    _WORK_URL = _ROOT + 'work/=/product_id/{}.html'
    _ANNOUNCE_URL = _ROOT + 'announce/=/product_id/{}.html'

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
        return str(
            soup.find(id="work_maker")
            .find(**{'class': 'maker_name'})
            .a.string)

    _series_pattern = re.compile('^シリーズ名')

    def _get_series(self, soup) -> str:
        """Get work series name."""
        try:
            return str(
                soup.find(id='work_outline')
                .find('th', string=self._series_pattern)
                .find_next_sibling('td')
                .a.string)
        except AttributeError:
            return ''

    def _get_page(self, rjcode: str) -> str:
        """Get webpage text for a work."""
        try:
            request = urllib.request.urlopen(self._get_work_url(rjcode))
        except urllib.error.HTTPError as e:
            if e.code != 404:
                raise
            request = urllib.request.urlopen(self._get_announce_url(rjcode))
        return request.read().decode()

    def _get_work_url(self, rjcode: str) -> str:
        """Get DLsite work URL corresponding to an RJ code."""
        return self._WORK_URL.format(rjcode)

    def _get_announce_url(self, rjcode: str) -> str:
        """Get DLsite announce URL corresponding to an RJ code."""
        return self._ANNOUNCE_URL.format(rjcode)


class CachedFetcher(WorkInfoFetcher):

    def __init__(self, path):
        super().__init__()
        path = pathlib.Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self._shelf = shelve.open(os.fspath(path))

    def __call__(self, rjcode: str) -> 'WorkInfo':
        try:
            return self._shelf[rjcode]
        except KeyError:
            work_info = super().__call__(rjcode)
            self._shelf[rjcode] = work_info
            return work_info

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self._shelf.close()


class WorkInfo:

    __slots__ = ('rjcode', 'name', 'maker', 'series')

    def __init__(self, rjcode, name, maker, series=''):
        self.rjcode = rjcode
        self.name = name
        self.maker = maker
        self.series = series

    def __str__(self):
        return f'{self.rjcode} [{self.maker}] {self.name}'

    @property
    def as_filename(self):
        return _escape_filename(str(self))

    @property
    def as_path(self):
        path = pathlib.PurePath(_escape_filename(self.maker))
        if self.series:
            path /= _escape_filename(self.series)
        path /= _escape_filename('%s %s' % (self.rjcode, self.name))
        return path


def _escape_filename(filename: str) -> str:
    return filename.replace('/', '_')


_CACHE = pathlib.Path.home() / '.cache' / 'mir.dlsite.db'


def get_fetcher():
    """Get default cached fetcher."""
    return CachedFetcher(_CACHE)
