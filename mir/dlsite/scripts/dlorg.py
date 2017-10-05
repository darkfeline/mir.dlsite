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

"""Organize DLsite works."""

import argparse
import logging
import os
from pathlib import Path
from typing import NamedTuple

from mir.dlsite import api
from mir.dlsite import rj

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level='DEBUG')

    parser = argparse.ArgumentParser()
    parser.add_argument('top_dir', nargs='?', default=Path.cwd(),
                        type=Path)
    parser.add_argument('-n', '--dry-run', action='store_true')
    parser.add_argument('-a', '--all', action='store_true')
    args = parser.parse_args()

    finder = _find_all if args.all else _find
    fixer = _dryrun_fix if args.dry_run else _fix

    works = finder(args.top_dir)
    renames = _calculate_path_renames(works)
    fixer(args.top_dir, renames)


def _find(top_dir: Path) -> 'Iterable[Path]':
    """Find DLsite work paths.

    Yield Path instances to work directories, relative to top_dir.
    """
    for path in top_dir.iterdir():
        if not path.is_dir():
            continue
        if rj.contains(path.name):
            yield path


def _find_all(top_dir: Path) -> 'Iterable[Path]':
    """Find DLsite work paths recursively.

    Yield Path instances to work directories, relative to top_dir.
    """
    for path in _walk_dirs(top_dir):
        if rj.contains(path.name):
            yield path


def _walk_dirs(top_dir: Path) -> 'Iterable[Path]':
    """Yield relative paths to all subdirs, recursively."""
    for dirpath, dirnames, _filenames in os.walk(top_dir):
        dirpath = Path(dirpath)
        for dirname in dirnames:
            yield (dirpath / dirname).relative_to(top_dir)


def _calculate_path_renames(works: 'Iterable[Path]') -> 'Iterable[_PathRename]':
    """Find work renames.

    Yield _PathRename instances.
    """
    with api.get_fetcher() as fetcher:
        for path in works:
            rjcode = rj.parse(path.name)
            work_info = fetcher(rjcode)
            yield _PathRename(path, work_info.as_path)


def _dryrun_fix(top_dir: Path, renames: 'Iterable[_PathRename]'):
    for rename in renames:
        if rename.is_noop():
            logger.debug('%s already correct', rename.old)
            continue
        logger.debug('Renaming %s to %s', rename.old, rename.new)


def _fix(top_dir: Path, renames: 'Iterable[_PathRename]'):
    for rename in renames:
        if rename.is_noop():
            logger.debug('%s already correct', rename.old)
            continue
        logger.debug('Renaming %s to %s', rename.old, rename.new)
        rename.execute(top_dir)
    _remove_empty_dirs(top_dir)


def _remove_empty_dirs(top_dir: Path):
    for dirpath, dirnames, filenames in os.walk(top_dir, topdown=False):
        if not (dirnames or filenames):
            os.rmdir(dirpath)


class _PathRename(NamedTuple):
    old: Path
    new: Path

    def __rtruediv__(self, other):
        if isinstance(other, Path):
            return _PathRename(
                old=other / self.old,
                new=other / self.new,
            )

    def is_noop(self):
        return self.old == self.new

    def execute(self, top_dir: Path):
        old = top_dir / self.old
        new = top_dir / self.new
        new.parent.mkdir(parents=True, exist_ok=True)
        old.rename(new)


if __name__ == '__main__':
    main()
