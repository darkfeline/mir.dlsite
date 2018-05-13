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

from pathlib import Path

import pytest

from mir.dlsite import workinfo


def test_parse_rjcode():
    assert workinfo.parse_rjcode('asdf RJ123 asdf') == 'RJ123'


def test_parse_rjcode_when_missing():
    with pytest.raises(ValueError):
        workinfo.parse_rjcode('asdf')


def test_contains_rjcode():
    assert workinfo.contains_rjcode('asdf RJ123 asdf')


def test_contains_rjcode_missing():
    assert not workinfo.contains_rjcode('asdf')


def test_work_repr():
    work = workinfo.Work('RJ123', 'foo', 'bar')
    got = repr(work)
    assert repr('RJ123') in got
    assert repr('foo') in got
    assert repr('bar') in got
    assert type(work).__qualname__ in got


def test_work_filename():
    obj = workinfo.Work('RJ123', 'foo', 'bar')
    assert workinfo.work_filename(obj) == 'RJ123 [bar] foo'


def test_work_filename_slash():
    obj = workinfo.Work('RJ123', 'foo/', 'bar')
    assert workinfo.work_filename(obj) == 'RJ123 [bar] foo_'


def test_work_path():
    obj = workinfo.Work('RJ123', 'foo', 'bar')
    assert workinfo.work_path(obj) == Path('bar/RJ123 foo')


def test_work_path_with_series():
    obj = workinfo.Work('RJ123', 'foo', 'bar')
    obj.series = 'baz'
    assert workinfo.work_path(obj) == Path('bar/baz/RJ123 foo')


def test_work_path_slash():
    obj = workinfo.Work('RJ123', 'foo', 'bar/')
    assert workinfo.work_path(obj) == Path('bar_/RJ123 foo')


def test_track_eq():
    track1 = workinfo.Track('lydie', 'suelle')
    track2 = workinfo.Track('lydie', 'suelle')
    assert track1 == track2


def test_track_not_eq():
    track1 = workinfo.Track('lydie', 'suelle')
    track2 = workinfo.Track('sophie', 'prachta')
    assert track1 != track2


def test_track_eq_wrong_type():
    track = workinfo.Track('lydie', 'suelle')
    assert track != 'asdf'
