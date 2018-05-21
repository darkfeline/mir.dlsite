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
import logging.config
import os
from pathlib import Path
import sys

from mir.dlsite import api
from mir.dlsite import workinfo

logger = logging.getLogger(__name__)


def main(argv):
    args = _parse_args(argv)
    _configure_logging()
    paths = _find_works(args.top_dir, recursive=args.all)
    if not args.all:
        paths = _filter_shallow_paths(paths)
    with api.get_fetcher() as fetcher:
        for path in paths:
            _do_one(args, fetcher, path)
    if not args.dry_run:
        logger.info('Removing empty dirs')
        _remove_empty_dirs(args.top_dir)


def _parse_args(argv):
    parser = argparse.ArgumentParser(prog=argv[0],
                                     description=__doc__)
    parser.add_argument('top_dir', nargs='?', default=Path.cwd(),
                        type=Path)
    parser.add_argument('-n', '--dry-run', action='store_true')
    parser.add_argument('-a', '--all', action='store_true')
    parser.add_argument('-d', '--add-descriptions', action='store_true')
    return parser.parse_args(argv[1:])


def _configure_logging():
    logging.config.dictConfig({
        'version': 1,
        'root': {
            'level': 'DEBUG',
            'handlers': ['default'],
        },
        'handlers': {
            'default': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
            },
        },
        'formatters': {
            'default': {
                'format': 'dlorg: %(asctime)s:%(levelname)s:%(name)s:%(message)s',
            },
        },
        'disable_existing_loggers': False,
    })


def _filter_shallow_paths(paths: 'Iterable[Path]'):
    """Filter keeping shallow paths."""
    for p in paths:
        if len(p.parts) == 1:
            yield p


def _find_works(top_dir: 'PathLike') -> 'Iterable[Path]':
    """Find DLsite works.

    Yield Path instances to work directories, relative to top_dir.
    """
    for dirpath, dirnames, _filenames in os.walk(top_dir):
        work_dirnames = [n for n in dirnames if workinfo.contains_rjcode(n)]
        yield from (Path(dirpath, n).relative_to(top_dir) for n in work_dirnames)
        for n in work_dirnames:
            dirnames.remove(n)


def _remove_empty_dirs(top_dir: 'PathLike'):
    for dirpath, dirnames, filenames in os.walk(top_dir, topdown=False):
        if not os.listdir(dirpath):
            os.rmdir(dirpath)


def _do_one(args, fetcher, path):
    new_path = _calculate_new_path(fetcher, path)
    if args.dry_run:
        if path != new_path:
            logger.info('Would rename %s to %s', path, new_path)
        return
    if path != new_path:
        _rename(args.top_dir, path, new_path)
        path = new_path
    if args.add_descriptions:
        logger.info('Adding description files for %s', path)
        _add_dlsite_files(fetcher, path)


def _calculate_new_path(fetcher, path: 'Path') -> 'Path':
    """Find rename operation to organize work."""
    rjcode = workinfo.parse_rjcode(path.name)
    work = fetcher(rjcode)
    return workinfo.work_path(work)


def _rename(top_dir: 'Path', old: 'Path', new: 'Path'):
    old = top_dir / old
    new = top_dir / new
    new.parent.mkdir(parents=True, exist_ok=True)
    logger.debug('Renaming %s to %s', old, new)
    old.rename(new)


_DESC_FILE = 'dlsite-description.txt'
_TRACK_FILE = 'dlsite-tracklist.txt'


def _add_dlsite_files(fetcher, path: 'Path'):
    """Add dlsite information files to a work."""
    rjcode = workinfo.parse_rjcode(path.name)
    work = fetcher(rjcode)
    desc_file = path / _DESC_FILE
    if not desc_file.exists() and work.description is not None:
        logger.info('Adding %s', desc_file)
        desc_file.write_text(work.description)
    track_file = path / _TRACK_FILE
    if not track_file.exists() and work.tracklist is not None:
        logger.info('Adding %s', track_file)
        tl = ''.join(f'{t.name} {t.text}\n' for t in work.tracklist)
        track_file.write_text(tl)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
