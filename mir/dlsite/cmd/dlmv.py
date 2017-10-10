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

"""Rename a file by dlsite code."""

import argparse
import os

from mir.dlsite import api
from mir.dlsite import workinfo


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file')
    parser.add_argument('rjcode', nargs='?', default=None,
                        type=workinfo.parse_rjcode)
    args = parser.parse_args()

    if args.rjcode is None:
        rjcode = workinfo.parse_rjcode(args.file)
    else:
        rjcode = args.rjcode

    with api.get_fetcher() as fetcher:
        work = fetcher(rjcode)
    os.rename(args.file, workinfo.work_filename(work))


if __name__ == '__main__':
    main()
