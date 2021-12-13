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

import logging
import os
from pathlib import Path
import re
import shelve
import urllib.request

import bs4
from bs4 import BeautifulSoup

from mir.dlsite import workinfo
from mir.dlsite.locale import Locale


logger = logging.getLogger(__name__)


def fetch_work(rjcode: str, locale: Locale = Locale.Japanese) -> workinfo.Work:
    """Fetch DLsite work information."""
    page = _get_page(rjcode, locale)
    soup = BeautifulSoup(page, 'lxml')
    work = workinfo.Work(
        rjcode=rjcode,
        locale=locale,
        name=_get_name(soup),
        maker=_get_maker(soup))
    work.description = _get_description(soup)
    work.images = list(_generate_images(soup))
    try:
        work.age = _get_age(soup)
    except _NoInfoError:
        pass
    try:
        series = _get_series(soup, locale)
    except _NoInfoError:
        pass
    else:
        work.series = series
    try:
        tracklist = list(_generate_tracklist(soup))
    except _NoInfoError:
        pass
    else:
        work.tracklist = tracklist
    try:
        work.genres = list(_generate_genres(soup))
    except _NoInfoError:
        pass
    return work


def _get_page(rjcode: str, locale: Locale) -> str:
    """Get webpage text for a work."""
    try:
        request = urllib.request.urlopen(_get_work_url(rjcode, locale))
    except urllib.error.HTTPError as e:
        if e.code != 404:  # pragma: no cover
            raise
        request = urllib.request.urlopen(_get_announce_url(rjcode))
    return request.read().decode()


_ROOT = 'https://www.dlsite.com/maniax/'
_LOCALE = '?locale={}'
_WORK_URL = _ROOT + 'work/=/product_id/{}.html' + _LOCALE
_ANNOUNCE_URL = _ROOT + 'announce/=/product_id/{}.html' + _LOCALE


def _get_work_url(rjcode: str, locale: Locale = Locale.Japanese) -> str:
    """Get DLsite work URL corresponding to an RJ code."""
    return _WORK_URL.format(rjcode, locale.value)


def _get_announce_url(rjcode: str, locale: Locale = Locale.Japanese) -> str:
    """Get DLsite announce URL corresponding to an RJ code."""
    return _ANNOUNCE_URL.format(rjcode, locale.value)


def _get_name(soup) -> str:
    """Get the work name."""
    return soup.find(id='work_name').a.contents[-1].strip()


def _get_maker(soup) -> str:
    """Get the work maker."""
    return str(
        soup.find(id="work_maker")
            .find(**{'class': 'maker_name'})
            .a.string)


_SERIES_PATTERN = {
    Locale.Japanese: re.compile('^シリーズ名'),
    Locale.English: re.compile('^Series name'),
    Locale.ChineseSimplified: re.compile('^系列名'),
    Locale.ChineseTraditional: re.compile('^系列名'),
    Locale.Korean: re.compile('^시리즈명'),
}



def _get_series(soup, locale: Locale) -> str:
    """Get work series name."""
    try:
        return str(
            soup.find(id='work_outline')
                .find('th', string=_SERIES_PATTERN[locale])
                .find_next_sibling('td')
                .a.string)
    except AttributeError:
        raise _NoInfoError('no series')


def _get_description(soup) -> str:
    """Get work description."""
    contents = (
        soup.find(id='main_inner')
            .find('div', itemprop='description')
            .strings)
    text = ''.join(_replace_br(contents))
    return text.strip() + '\n'


def _generate_images(soup) -> 'Iterable[str]':
    div = soup.find('div', {'class': 'product-slider-data'})
    image_div = div.find_all('div')
    for image in image_div:
        yield 'https:' + image['data-src']


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


def _get_age(soup) -> workinfo.AgeRating:
    """Get work age rating."""
    work_block = soup.find(id='work_outline')
    if work_block.find('span', {'class': 'icon_GEN'}) is not None:
        return workinfo.AgeRating.AllAges
    elif work_block.find('span', {'class': 'icon_R15'}) is not None:
        return workinfo.AgeRating.R15
    elif work_block.find('span', {'class': 'icon_ADL'}) is not None:
        return workinfo.AgeRating.R18
    else:
        raise _NoInfoError('no age rating')  # can this even happen?


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


def _generate_genres(soup) -> 'Iterable[str]':
    div = soup.find('div', {'class': 'main_genre'})
    if div is None:
        raise _NoInfoError('no genre')
    a_list = div.find_all('a')
    if a_list is None:
        raise _NoInfoError('no genre')
    for a in a_list:
        yield a.text


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

    def __call__(self, rjcode: str, locale: Locale = Locale.Japanese) -> workinfo.Work:
        try:
            return self._shelf[rjcode + '-' + locale.value]
        except TypeError:
            raise ValueError('called unopened CachedFetcher')
        except KeyError:
            work = self._fetcher(rjcode, locale)
            self._shelf[rjcode + '-' + locale.value] = work
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
