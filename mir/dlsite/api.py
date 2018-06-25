# Copyright (C) 2016, 2017, 2018 Allen Li
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

import logging
import os
from pathlib import Path
import re
import shelve
import urllib.request

import bs4
from bs4 import BeautifulSoup

from mir.dlsite import workinfo

logger = logging.getLogger(__name__)


def fetch_work(rjcode: str) -> workinfo.Work:
    """Fetch DLsite work information."""
    page = _get_page(rjcode)
    soup = BeautifulSoup(page, 'lxml')
    work = workinfo.Work(
        rjcode=rjcode,
        name=_get_name(soup),
        maker=_get_maker(soup))
    work.description = _get_description(soup)
    work.age_rating = _get_age_rating(soup)
    work.genre = _get_genre(soup)
    try:
        series = _get_series(soup)
    except _NoInfoError:
        pass
    else:
        work.series = series
    try:
        tracklist = _get_tracklist(soup)
    except _NoInfoError:
        pass
    else:
        work.tracklist = tracklist
    return work


def _get_page(rjcode: str) -> str:
    """Get webpage text for a work."""
    try:
        request = urllib.request.urlopen(_get_work_url(rjcode))
    except urllib.error.HTTPError as e:
        if e.code != 404:  # pragma: no cover
            raise
        request = urllib.request.urlopen(_get_announce_url(rjcode))
    return request.read().decode()


_ROOT = 'http://www.dlsite.com/maniax/'
_WORK_URL = _ROOT + 'work/=/product_id/{}.html'
_ANNOUNCE_URL = _ROOT + 'announce/=/product_id/{}.html'


def _get_work_url(rjcode: str) -> str:
    """Get DLsite work URL corresponding to an RJ code."""
    return _WORK_URL.format(rjcode)


def _get_announce_url(rjcode: str) -> str:
    """Get DLsite announce URL corresponding to an RJ code."""
    return _ANNOUNCE_URL.format(rjcode)


def _get_name(soup) -> str:
    """Get the work name."""
    return soup.find(id='work_name').a.contents[-1].strip()


def _get_maker(soup) -> str:
    """Get the work maker."""
    return str(
        soup.find(id="work_maker")
        .find(**{'class': 'maker_name'})
        .a.string)


_SERIES_PATTERN = re.compile('^Series|^シリーズ名')


def _get_series(soup) -> str:
    """Get work series name."""
    try:
        return str(
            soup.find(id='work_outline')
            .find('th', string=_SERIES_PATTERN)
            .find_next_sibling('td')
            .a.string)
    except AttributeError:
        raise _NoInfoError('no series')


_AGE_RATING_PATTERN = re.compile('^Age Ratings|^年齢指定')


def _is_age_rating(tag) -> bool:
    """BeautifulSoup match function for age rating."""
    return (tag.get('class') == ['work_genre']
        and _AGE_RATING_PATTERN.search(tag.parent.parent.th.string))


def _get_age_rating(soup) -> str:
    """Get work age rating."""
    return soup.find(_is_age_rating).string


_GENRE_PATTERN = re.compile('^Genre|^ジャンル')


def _is_genre(tag) -> bool:
    """BeautifulSoup match function for genre."""
    return (tag.get('class') == ['main_genre']
        and _GENRE_PATTERN.search(tag.parent.parent.th.string))


def _get_genre(soup) -> list:
    """Get work genre."""
    return [a.string for a in soup.find(_is_genre).find_all('a')]


def _get_description(soup) -> str:
    """Get work series name."""
    contents = (
        soup.find(id='main_inner')
        .find('div', itemprop='description')
        .contents)
    text = ''.join(_replace_br(contents))
    return text.strip() + '\n'


def _replace_br(elements) -> 'Iterable[str]':
    """Replace br tags with newline strings."""
    for element in elements:
        if not isinstance(element, bs4.element.Tag):
            yield element
            continue
        if element.name == 'br':
            # DLSite includes redundant <br/>
            continue
        logger.debug('Encountered unhandled tag %r', element)
        yield element.string


def _get_tracklist(soup) -> 'List[Track]':
    return list(_generate_tracklist(soup))


def _generate_tracklist(soup) -> 'Iterable[Track]':
    div = soup.find('div', id='work_parts')
    if div is None:
        raise _NoInfoError('no tracklist')
    ol = div.find('ol', {'class': 'work_tracklist_list'})
    if ol is None:
        raise _NoInfoError('no tracklist')
    li_list = ol.find_all('li')
    for li in li_list:
        name = ' '.join(li.find('p', {'class': 'track_name'}).strings)
        text = str(li.find('p', {'class': 'track_text'}).string)
        yield workinfo.Track(name, text)


class CachedFetcher:

    """DLSite work fetcher that uses a cache.

    CachedFetcher does not implement fetching and needs to be passed a
    fetching function like fetch_work().

    CachedFetcher uses Python's shelve module for caching.
    """

    def __init__(self, path: 'PathLike', fetcher):
        self._fetcher = fetcher
        self._path = path
        self._shelf = None

    def __call__(self, rjcode: str) -> workinfo.Work:
        try:
            return self._shelf[rjcode]
        except TypeError:
            raise ValueError('called unopened CachedFetcher')
        except KeyError:
            work = self._fetcher(rjcode)
            self._shelf[rjcode] = work
            return work

    def __enter__(self):
        self._shelf = shelve.open(os.fspath(self._path))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self._shelf.close()


class _NoInfoError(ValueError):
    """No info found."""


_CACHE = Path.home() / '.cache' / 'mir.dlsite.db'


def get_fetcher():
    """Create a default CachedFetcher instance."""
    path = Path(_CACHE)
    path.parent.mkdir(parents=True, exist_ok=True)
    return CachedFetcher(_CACHE, fetch_work)
