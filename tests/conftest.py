# Copyright (C) 2018 Allen Li
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

from unittest import mock

import pytest

from mir.dlsite import workinfo
from mir.dlsite.workinfo import Track


@pytest.fixture
def patch_fetcher(stub_fetcher):
    with mock.patch('mir.dlsite.api.get_fetcher') as get_fetcher:
        get_fetcher.return_value = stub_fetcher
        yield get_fetcher


@pytest.fixture
def stub_fetcher():
    def fetch(rjcode):
        work = workinfo.Work(rjcode, 'name', 'group')
        work.series = 'series'
        return work
    return _Fetcher(fetch)


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
    return _Fetcher(fetch)


class _Fetcher:

    def __init__(self, func):
        self._func = func

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def __call__(self, rjcode):
        return self._func(rjcode)
