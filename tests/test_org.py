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


def test_remove_empty_dirs(tmpdir):
    tmpdir.ensure('foo/bar/baz/sophie', dir=True)
    tmpdir.ensure('foo/spam')

    org.remove_empty_dirs(str(tmpdir))

    assert os.listdir(str(tmpdir)) == ['foo']
    assert os.listdir(str(tmpdir.join('foo'))) == ['spam']


def test_PathRename_execute(tmpdir):
    tmpdir.ensure('foo/bar/baz/sophie')
    r = org.PathRename(Path('foo/bar/baz'),
                       Path('baz'))
    r.execute(Path(str(tmpdir)))
    assert os.path.exists(os.path.join(str(tmpdir), 'baz/sophie'))


def test_apply_renames():
    paths = [
        Path('foo/bar'),
        Path('sophie/prachta'),
    ]
    renames = [
        PathRename(Path('foo/bar'), Path('lydie/suelle')),
        PathRename(Path('fujiwara/takeda'), Path('hotaru/yuma')),
    ]
    got = list(org.apply_renames(paths, renames))
    assert got == [
        Path('lydie/suelle'),
        Path('sophie/prachta'),
    ]


@pytest.fixture
def stub_fetcher():
    def fetch(rjcode):
        work = workinfo.Work(rjcode, 'name', 'group')
        work.series = 'series'
        return work
    return fetch
