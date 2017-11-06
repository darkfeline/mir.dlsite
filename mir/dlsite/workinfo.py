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

"""DLSite work info library"""

from pathlib import Path
import re

_RJCODE_PATTERN = re.compile(r'RJ[0-9]+')


def parse_rjcode(string) -> str:
    """Parse RJ code from a string."""
    match = _RJCODE_PATTERN.search(string)
    if match is None:
        raise ValueError('No rjcode found.')
    return match.group(0)


def contains_rjcode(string) -> bool:
    """Return True if an RJ code is inside string."""
    return bool(_RJCODE_PATTERN.search(string))


class Work:
    """DLSite work info data class."""

    rjcode: str
    name: str
    maker: str
    series: 'Optional[str]'
    description: 'Optional[str]'
    tracklist: 'Optional[List[Track]]'

    def __init__(self, rjcode, name, maker):
        self.rjcode = rjcode
        self.name = name
        self.maker = maker
        self.series = None
        self.description = None
        self.tracklist = None

    def __repr__(self):
        cls = type(self).__qualname__
        return (f'<{cls} with rjcode={self.rjcode!r}, name={self.name!r},'
                f' maker={self.maker!r}, series={self.series!r}>')

    def __str__(self):
        return f'{self.rjcode} [{self.maker}] {self.name}'


def work_filename(work) -> str:
    """Return the standalone filename to be used for a work."""
    return _escape_filename(f'{work.rjcode} [{work.maker}] {work.name}')


def work_path(work) -> Path:
    """Return the path to be used for a work."""
    path = Path(_escape_filename(work.maker))
    if work.series:
        path /= _escape_filename(work.series)
    path /= _escape_filename(f'{work.rjcode} {work.name}')
    return path


class Track:
    """DLSite track info data class."""

    name: str
    text: str

    def __init__(self, name, text):
        self.name = name
        self.text = text

    def __repr__(self):
        cls = type(self).__qualname__
        return (f'{cls}({self.name!r}, {self.text!r})')

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return (self.name == other.name
                    and self.text == other.text)
        return NotImplemented


def _escape_filename(filename: str) -> str:
    return filename.replace('/', '_')
