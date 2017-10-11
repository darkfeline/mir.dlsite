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
from pathlib import Path

from mir.dlsite import org

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level='DEBUG')

    parser = argparse.ArgumentParser()
    parser.add_argument('top_dir', nargs='?', default=Path.cwd(),
                        type=Path)
    parser.add_argument('-n', '--dry-run', action='store_true')
    parser.add_argument('-a', '--all', action='store_true')
    args = parser.parse_args()

    paths = list(org.find_works(args.top_dir))
    if not args.all:
        paths = [p for p in paths if len(p.parts) == 1]

    renames = list(org.calculate_path_renames(paths))
    if args.dry_run:
        for r in renames:
            logger.info('Would rename %s to %s', r.old, r.new)
        ...
    else:
        for r in renames:
            r.execute(args.top_dir)
        org.remove_empty_dirs(args.top_dir)
        paths = org.apply_renames(paths, renames)
        ...


if __name__ == '__main__':
    main()
