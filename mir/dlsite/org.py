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

"""Organizing works."""

import logging
import os
from pathlib import Path
from typing import NamedTuple

from mir.dlsite import workinfo

logger = logging.getLogger(__name__)


def find_works(top_dir: 'PathLike') -> 'Iterable[Path]':
    """Find DLsite works.

    Yield Path instances to work directories, relative to top_dir.
    """
    for dirpath, dirnames, _filenames in os.walk(top_dir):
        work_dirnames = [n for n in dirnames if workinfo.contains_rjcode(n)]
        yield from (Path(dirpath, n).relative_to(top_dir) for n in work_dirnames)
        for n in work_dirnames:
            dirnames.remove(n)


def calculate_path_renames(fetcher, paths: 'Iterable[Path]') -> 'Iterable[PathRename]':
    """Find rename operations to organize works.

    Yield PathRename instances.
    """
    for path in paths:
        rjcode = workinfo.parse_rjcode(path.name)
        work = fetcher(rjcode)
        wanted_path = workinfo.work_path(work)
        if path != wanted_path:
            yield PathRename(path, wanted_path)
        else:
            logger.info('%s already correct', path)


def remove_empty_dirs(top_dir: 'PathLike'):
    for dirpath, dirnames, filenames in os.walk(top_dir, topdown=False):
        if not os.listdir(dirpath):
            os.rmdir(dirpath)


class PathRename(NamedTuple):
    """PathRename represents a rename operation."""
    old: Path
    new: Path

    def execute(self, top_dir: Path):
        old = top_dir / self.old
        new = top_dir / self.new
        new.parent.mkdir(parents=True, exist_ok=True)
        logger.debug('Renaming %s to %s', old, new)
        old.rename(new)


def apply_renames(paths: 'Iterable[Path]',
                  renames: 'Iterable[PathRename]') -> 'List[Path]':
    """Apply PathRenames to Paths."""
    renames_map = {r.old: r.new for r in renames}
    return [renames_map.get(p, p) for p in paths]


_DESC_FILE = 'dlsite-description.txt'
_TRACK_FILE = 'dlsite-tracklist.txt'


def add_dlsite_files(fetcher, path: Path):
    """Add dlsite information files to a work."""
    rjcode = workinfo.parse_rjcode(path.name)
    work = fetcher(rjcode)
    desc_file = path / _DESC_FILE
    if not desc_file.exists() and work.description is not None:
        desc_file.write_text(work.description)
    track_file = path / _TRACK_FILE
    if not track_file.exists() and work.tracklist is not None:
        tl = ''.join(f'{t.name} {t.text}\n' for t in work.tracklist)
        track_file.write_text(tl)
