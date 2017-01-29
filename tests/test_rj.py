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

import pytest

from mir.dlsite import rj


def test_parse():
    assert rj.parse('asdf RJ123 asdf') == 'RJ123'


def test_parse_missing():
    with pytest.raises(ValueError):
        rj.parse('asdf')


def test_contains():
    assert rj.contains('asdf RJ123 asdf')


def test_contains_missing():
    assert not rj.contains('asdf')
