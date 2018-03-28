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
import logging
from unittest import mock
import re
import urllib.error

import pathlib

import pytest

from mir.dlsite import api
from mir.dlsite.workinfo import Track

logger = logging.getLogger(__name__)


def test_get_work_url():
    got = api._get_work_url('RJ123')
    assert got == 'http://www.dlsite.com/maniax/work/=/product_id/RJ123.html'


def test_get_announce_url():
    got = api._get_announce_url('RJ123')
    assert got == 'http://www.dlsite.com/maniax/announce/=/product_id/RJ123.html'


def test_fetch_work_with_series(fake_urlopen):
    work = api.fetch_work('RJ189758')
    assert work.rjcode == 'RJ189758'
    assert work.maker == 'B-bishop'
    assert work.name == '意地悪な機械人形に完全支配される音声 地獄級射精禁止オナニーサポート4 ヘルエグゼキューション'
    assert work.series == '地獄級オナニーサポート'
    assert work.description.startswith('''皆様、こんにちは。サークルB-bishopのpawnlank7と申します。
今作は、地獄級に激しいオナニーサポート作品第4弾です。
''')
    assert work.description.endswith('''本作品の販売
B-bishop http://pawnlank7.blog.fc2.com
''')


def test_fetch_work_without_series(fake_urlopen):
    work = api.fetch_work('RJ173248')
    assert work.rjcode == 'RJ173248'
    assert work.maker == 'B-bishop'
    assert work.name == '搾精天使ピュアミルク 背後からバイノーラルでいじめられる音声'
    assert work.series is None


def test_fetch_work_with_tracklist(fake_urlopen):
    work = api.fetch_work('RJ126928')
    assert work.rjcode == 'RJ126928'
    assert work.maker == 'クッキーボイス'
    assert work.name == 'まじこスハロウィン -可愛い彼女は吸血鬼!? 妖しく光る魅了の魔眼の巻-'
    assert work.tracklist == [
        Track('1. WELCOME\u3000TO\u3000HALLOWEEN',
              '『ハロウィンの招待状』\u3000約1分\u3000※BGMの有無選択可能'),
        Track('2. 魅了吸血お漏らし', '『ヒロインの来訪、魅了束縛でのイタズラ』\u3000約18分'),
        Track('3. フェラチオきば愛情', '『精液を摂取する、吸血鬼』\t約16分'),
        Track('4. あなたもう゛ぁんぷ', '『童貞卒業、牙で噛み合い』\t約15分'),
        Track('5. 突発ラジオ', '『ラブラブ朝のグッドモーニング放送局』\t約6分'),
    ]
    assert type(work.tracklist[0].text) is str


def test_fetch_work_from_announce(fake_urlopen):
    work = api.fetch_work('RJ189666')
    assert work.rjcode == 'RJ189666'
    assert work.maker == 'S彼女'
    assert work.name == '強気な妹に連射させられる!? ～即ヌキ淫語16～'
    assert work.series == '即ヌキ淫語'


def test_cached_fetcher_used_without_context(tmpdir, fake_urlopen):
    fetcher = api.CachedFetcher(str(tmpdir.join('cache')), api.fetch_work)
    with pytest.raises(ValueError):
        fetcher('RJ189758')


def test_cached_fetcher(tmpdir, fake_urlopen):
    fetcher = api.CachedFetcher(str(tmpdir.join('cache')), api.fetch_work)
    with fetcher:
        work1 = fetcher('RJ189758')
        fake_urlopen.side_effect = _FakeError
        work2 = fetcher('RJ189758')
    assert work1.rjcode == work2.rjcode


def _get_page(section: str, rjcode: str) -> str:
    """Get test page contents as a fake HTTP body."""
    logger.debug(f'Getting page {section} {rjcode}')
    path = (pathlib.Path(__file__).parent
            / 'pages' / section / f'{rjcode}.html')
    try:
        text = path.read_text()
    except FileNotFoundError:
        raise _FakeError
    return io.BytesIO(text.encode())


def _open_url(url):
    """Fake DLSite URL open."""
    logger.debug(f'Opening {url}')
    match = re.match(r'http://www.dlsite.com/maniax/(work|announce)/=/product_id/(RJ[0-9]+)(.html)?',
                     url)
    if match is None:  # pragma: no cover
        raise _FakeError
    return _get_page(match.group(1), match.group(2))


@pytest.fixture
def fake_urlopen():
    with mock.patch('urllib.request.urlopen') as urlopen:
        urlopen.side_effect = _open_url
        yield urlopen


class _FakeError(urllib.error.HTTPError):

    def __init__(self):
        self.code = 404
