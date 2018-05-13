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

from mir.dlsite import org
from mir.dlsite.org import PathRename
from mir.dlsite import workinfo
from mir.dlsite.workinfo import Track


def test_find_works(tmpdir):
    tmpdir.ensure('foo/RJ123/RJ456', dir=True)
    got = list(org.find_works(str(tmpdir)))
    assert got == [
        Path('foo/RJ123'),
    ]


def test_calculate_path_renames(stub_fetcher):
    works = [
        Path('foo/RJ123'),
        Path('group/series/RJ456 name'),
    ]
    got = list(org.calculate_path_renames(stub_fetcher, works))
    assert got == [
        PathRename(Path('foo/RJ123'), Path('group/series/RJ123 name')),
    ]


def test_do_path_renames(tmpdir):
    tmpdir.ensure('foo/bar/baz/sophie')
    r = org.PathRename(Path('foo/bar/baz'),
                       Path('baz'))
    org.do_path_renames(Path(str(tmpdir)), [r])
    assert os.path.exists(os.path.join(str(tmpdir), 'baz/sophie'))


def test_remove_empty_dirs(tmpdir):
    tmpdir.ensure('foo/bar/baz/sophie', dir=True)
    tmpdir.ensure('foo/spam')

    org.remove_empty_dirs(str(tmpdir))

    assert os.listdir(str(tmpdir)) == ['foo']
    assert os.listdir(str(tmpdir.join('foo'))) == ['spam']


def test_apply_renames():
    paths = [
        Path('foo/bar'),
        Path('sophie/prachta'),
    ]
    renames = [
        PathRename(Path('foo/bar'), Path('lydie/suelle')),
        PathRename(Path('fujiwara/takeda'), Path('hotaru/yuma')),
    ]
    got = org.apply_renames(paths, renames)
    assert got == [
        Path('lydie/suelle'),
        Path('sophie/prachta'),
    ]


def test_add_dlsite_files(tmpdir, fat_stub_fetcher):
    tmpdir.ensure('RJ123', dir=True)
    p = Path(str(tmpdir), 'RJ123')
    org.add_dlsite_files(fat_stub_fetcher, p)
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


def test_add_dlsite_files_does_not_overwrite(tmpdir, fat_stub_fetcher):
    tmpdir.ensure('RJ123/dlsite-description.txt').write('asdf')
    p = Path(str(tmpdir), 'RJ123')
    org.add_dlsite_files(fat_stub_fetcher, p)
    assert (p / 'dlsite-description.txt').read_text() == 'asdf'


def test_add_dlsite_files_missing_workinfo(tmpdir, stub_fetcher):
    tmpdir.ensure('RJ123', dir=True)
    p = Path(str(tmpdir), 'RJ123')
    org.add_dlsite_files(stub_fetcher, p)
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
