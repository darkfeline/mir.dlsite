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


def parse(string) -> str:
    """Parse RJ code from a string."""
    match = _RJCODE_PATTERN.search(string)
    if match is None:
        raise ValueError('No rjcode found.')
    return match.group(0)


def inside(string) -> bool:
    """Return True if an RJ code is inside string."""
    return bool(_RJCODE_PATTERN.search(string))
