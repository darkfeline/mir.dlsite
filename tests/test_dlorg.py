# Copyright (C) 2017 Allen Li
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

import os
from pathlib import Path

import pytest

from mir.dlsite.cmd import dlorg
from mir.dlsite import workinfo
from mir.dlsite.workinfo import Track


def test__find_works(tmpdir):
    tmpdir.ensure('foo/RJ123/RJ456', dir=True)
    got = list(dlorg._find_works(str(tmpdir)))
    assert got == [
        Path('foo/RJ123'),
    ]


def test__calculate_new_path(stub_fetcher):
    work = Path('foo/RJ123')
    got = dlorg._calculate_new_path(stub_fetcher, work)
    assert got == Path('group/series/RJ123 name')


def test_do__rename(tmpdir):
    tmpdir.ensure('foo/bar/baz/sophie')
    dlorg._rename(Path(str(tmpdir)), Path('foo/bar/baz'), Path('baz'))
    assert os.path.exists(os.path.join(str(tmpdir), 'baz/sophie'))


def test__remove_empty_dirs(tmpdir):
    tmpdir.ensure('foo/bar/baz/sophie', dir=True)
    tmpdir.ensure('foo/spam')

    dlorg._remove_empty_dirs(str(tmpdir))

    assert os.listdir(str(tmpdir)) == ['foo']
    assert os.listdir(str(tmpdir.join('foo'))) == ['spam']


def test__add_dlsite_files(tmpdir, fat_stub_fetcher):
    tmpdir.ensure('RJ123', dir=True)
    p = Path(str(tmpdir), 'RJ123')
    dlorg._add_dlsite_files(fat_stub_fetcher, p)
    assert (p / 'dlsite-description.txt').exists()
    assert (p / 'dlsite-description.txt').read_text() == '''\
Some text

Other text
'''
    assert (p / 'dlsite-tracklist.txt').exists()
    assert (p / 'dlsite-tracklist.txt').read_text() == '''\
1. foo bar
2. spam eggs
'''


def test__add_dlsite_files_does_not_overwrite(tmpdir, fat_stub_fetcher):
    tmpdir.ensure('RJ123/dlsite-description.txt').write('asdf')
    p = Path(str(tmpdir), 'RJ123')
    dlorg._add_dlsite_files(fat_stub_fetcher, p)
    assert (p / 'dlsite-description.txt').read_text() == 'asdf'


def test__add_dlsite_files_missing_workinfo(tmpdir, stub_fetcher):
    tmpdir.ensure('RJ123', dir=True)
    p = Path(str(tmpdir), 'RJ123')
    dlorg._add_dlsite_files(stub_fetcher, p)
    assert not (p / 'dlsite-description.txt').exists()
    assert not (p / 'dlsite-tracklist.txt').exists()


@pytest.fixture
def stub_fetcher():
    def fetch(rjcode):
        work = workinfo.Work(rjcode, 'name', 'group')
        work.series = 'series'
        return work
    return fetch


@pytest.fixture
def fat_stub_fetcher():
    def fetch(rjcode):
        work = workinfo.Work(rjcode, 'name', 'group')
        work.series = 'series'
        work.description = '''\
Some text

Other text
'''
        work.tracklist = [
            Track('1. foo', 'bar'),
            Track('2. spam', 'eggs'),
        ]
        return work
    return fetch
