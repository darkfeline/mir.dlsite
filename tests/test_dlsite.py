# Copyright (C) 2016 Allen Li
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

from mir import dlsite


def test_parse_rjcode():
    assert dlsite.parse_rjcode('asdf RJ123 asdf') == 'RJ123'


def test_parse_rjcode_missing():
    with pytest.raises(ValueError):
        dlsite.parse_rjcode('asdf')


def test_parse_rjcodes():
    assert list(dlsite.parse_rjcodes('RJ1 RJ2 RJ3')) == ['RJ1', 'RJ2', 'RJ3']


def test_parse_rjcodes_missing():
    assert list(dlsite.parse_rjcodes('asdf')) == []


def test_work_info_str():
    assert str(dlsite.WorkInfo('RJ123', 'foo', 'bar')) == 'RJ123 [bar] foo'
