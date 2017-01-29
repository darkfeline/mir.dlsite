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

"""RJ codes."""

import re

_RJCODE_PATTERN = re.compile(r'RJ[0-9]+')


def parse_rjcodes(string) -> 'Iterable':
    """Parse all RJ codes from a string."""
    for match in _RJCODE_PATTERN.finditer(string):
        yield match.group(0)


def parse_rjcode(string) -> str:
    """Parse RJ code from a string."""
    try:
        return next(parse_rjcodes(string))
    except StopIteration:
        raise ValueError('No rjcode found.')
