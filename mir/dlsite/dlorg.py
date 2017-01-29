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

import abc
import argparse
import logging
import os
import pathlib

from mir.dlsite import api
from mir.dlsite import rj

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level='DEBUG')

    parser = argparse.ArgumentParser()
    parser.add_argument('top_dir', nargs='?', default=pathlib.Path.cwd(),
                        type=pathlib.Path)
    parser.add_argument('-n', '--dry-run', action='store_true')
    args = parser.parse_args()

    fixer = DryRunFixer if args.dry_run else Fixer
    fixer(args.top_dir)()


class BaseFixer(abc.ABC):

    def __init__(self, top_dir: 'PathLike'):
        self._top_dir = pathlib.Path(top_dir)

    def __call__(self):
        renames = self._find_path_renames()
        self._fix(renames)

    @abc.abstractmethod
    def _fix(self, renames: 'Iterable[_PathRename]'):
        """Fix paths."""

    def _find_path_renames(self):
        """Find work renames.

        Yield _PathRename instances.
        """
        with api.get_fetcher() as fetcher:
            for current_path in self._find_works():
                rjcode = rj.parse(current_path.name)
                work_info = fetcher(rjcode)
                yield _PathRename(current_path, work_info.as_path)

    def _find_works(self) -> 'Iterable[Path]':
        """Find DLsite work paths.

        Yield Path instances to work directories, relative to top_dir.
        """
        for dirpath in _walk_dirs(self._top_dir):
            if rj.contains(dirpath.name):
                yield dirpath


def _walk_dirs(top_dir):
    """Yield relative paths to all subdirs, recursively."""
    for dirpath, dirnames, _filenames in os.walk(top_dir):
        dirpath = pathlib.Path(dirpath)
        for dirname in dirnames:
            yield (dirpath / dirname).relative_to(top_dir)


class DryRunFixer(BaseFixer):

    def _fix(self, renames):
        for rename in renames:
            if rename.needs_fix:
                logger.debug('%s already correct', rename.old)
                continue
            logger.debug('Renaming %s to %s', rename.old, rename.new)


class Fixer(BaseFixer):

    def _fix(self, renames):
        for rename in renames:
            if rename.needs_fix:
                logger.debug('%s already correct', rename.old)
                continue
            logger.debug('Renaming %s to %s', rename.old, rename.new)
            rename(self._top_dir)
        _remove_empty_dirs(self._top_dir)


def _remove_empty_dirs(top_dir: 'PathLike'):
    for dirpath, dirnames, filenames in os.walk(top_dir, topdown=False):
        if not (dirnames or filenames):
            os.rmdir(dirpath)


class _PathRename:

    """Represents a path rename operation."""

    __slots__ = ('old', 'new')

    def __init__(self, old, new):
        self.old = old
        self.new = new

    def __repr__(self):
        cls = type(self).__qualname__
        return f'{cls}({self.old!r}, {self.new!r})'

    def __call__(self, top_dir: 'PathLike'):
        top_dir = pathlib.Path(top_dir)
        old = top_dir / self.old
        new = top_dir / self.new
        new.parent.mkdir(parents=True, exist_ok=True)
        old.rename(new)

    @property
    def needs_fix(self):
        return self.old == self.new


if __name__ == '__main__':
    main()
