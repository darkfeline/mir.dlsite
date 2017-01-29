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

import io
from unittest import mock
import urllib.error

import pathlib

import pytest

from mir.dlsite import api


def test_get_work_url():
    fetcher = api.WorkInfoFetcher()
    assert fetcher._get_work_url('RJ123') == \
        'http://www.dlsite.com/maniax/work/=/product_id/RJ123.html'


def test_get_announce_url():
    fetcher = api.WorkInfoFetcher()
    assert fetcher._get_announce_url('RJ123') == \
        'http://www.dlsite.com/maniax/announce/=/product_id/RJ123.html'


@mock.patch('urllib.request.urlopen', autospec=True)
def test_get_page_work(urlopen):
    urlopen.return_value = io.BytesIO(b'foo')
    fetcher = api.WorkInfoFetcher()
    assert fetcher._get_page('RJ123') == 'foo'


@mock.patch('urllib.request.urlopen', autospec=True)
def test_get_page_announce(urlopen):
    urlopen.side_effect = _announce_opener(io.BytesIO(b'foo'))
    fetcher = api.WorkInfoFetcher()
    assert fetcher._get_page('RJ123') == 'foo'


@mock.patch('urllib.request.urlopen', autospec=True)
def test_get_page_error(urlopen):
    urlopen.side_effect = _error_opener
    fetcher = api.WorkInfoFetcher()
    with pytest.raises(urllib.error.HTTPError):
        fetcher._get_page('RJ123')


def _announce_opener(value):
    """A stub urlopen."""
    def opener(url):
        if 'announce' in url:
            return value
        else:
            raise urllib.error.HTTPError(
                url=url,
                code=404,
                msg='',
                hdrs=None,
                fp=None)
    return opener


def _error_opener(url):
    """A stub urlopen."""
    raise urllib.error.HTTPError(
        url=url,
        code=400,
        msg='',
        hdrs=None,
        fp=None)


def test_fetch_work_with_series():
    fetcher = _FakeFetcher()
    work_info = fetcher('RJ189758')
    assert work_info.rjcode == 'RJ189758'
    assert work_info.maker == 'B-bishop'
    assert work_info.name == '意地悪な機械人形に完全支配される音声 地獄級射精禁止オナニーサポート4 ヘルエグゼキューション'
    assert work_info.series == '地獄級オナニーサポート'


def test_fetch_work_without_series():
    fetcher = _FakeFetcher()
    work_info = fetcher('RJ173248')
    assert work_info.rjcode == 'RJ173248'
    assert work_info.maker == 'B-bishop'
    assert work_info.name == '搾精天使ピュアミルク 背後からバイノーラルでいじめられる音声'
    assert work_info.series == ''


def test_cached_fetcher(tmpdir):
    with _FakeCachedFetcher(tmpdir / 'cache') as fetcher:
        work_info = fetcher('RJ173248')
    assert work_info.rjcode == 'RJ173248'

    with mock.patch.object(_FakeCachedFetcher, '_get_page') as getter_mock, \
         _FakeCachedFetcher(tmpdir / 'cache') as fetcher:
        work_info = fetcher('RJ173248')
    assert work_info.rjcode == 'RJ173248'
    getter_mock.assert_not_called()


def test_work_info_str():
    assert str(api.WorkInfo('RJ123', 'foo', 'bar')) == 'RJ123 [bar] foo'


class _FakeFetcher(api.WorkInfoFetcher):

    def _get_page(self, rjcode):
        return (pathlib.Path(__file__).parent
                / 'pages' / ('%s.html' % rjcode)).read_text()


class _FakeCachedFetcher(_FakeFetcher, api.CachedFetcher):
    pass
