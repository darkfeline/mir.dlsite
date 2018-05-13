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
from pathlib import Path
import sys

from mir.dlsite import api
from mir.dlsite import org

logger = logging.getLogger(__name__)


def main(argv):
    args = _parse_args(argv)
    _configure_logging()
    paths = _find_works(args.top_dir, recursive=args.all)
    renames = _calculate_renames(paths)
    if args.dry_run:
        for r in renames:
            logger.info('Would rename %s to %s', r.old, r.new)
        return
    org.do_path_renames(args.top_dir, renames)
    logger.info('Removing empty dirs')
    org.remove_empty_dirs(args.top_dir)
    if args.add_descriptions:
        logger.info('Adding description files')
        new_paths = org.apply_renames(paths, renames)
        _add_dlsite_files(new_paths)


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


def _find_works(top_dir, recursive):
    paths = list(org.find_works(top_dir))
    if not recursive:
        paths = [p for p in paths if len(p.parts) == 1]
    return paths


def _calculate_renames(paths):
    with api.get_fetcher() as fetcher:
        return list(org.calculate_path_renames(fetcher, paths))


def _add_dlsite_files(paths):
    with api.get_fetcher() as fetcher:
        for p in paths:
            org.add_dlsite_files(fetcher, p)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
