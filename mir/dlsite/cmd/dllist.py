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

"""For each input line, look for rjcode and fetch dlsite info."""

import argparse
import sys

from mir.dlsite import api
from mir.dlsite import workinfo


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-info', action="store_true",
                        help="Do not fetch info; print RJ code only.")
    args = parser.parse_args()

    if args.no_info:
        printer = _simple_printer
    else:
        printer = _info_printer

    for line in sys.stdin:
        try:
            rjcode = workinfo.parse_rjcode(line)
        except ValueError:
            continue
        printer(rjcode)


def _simple_printer(rjcode: str):
    print(rjcode)


def _info_printer(rjcode: str):
    with api.get_fetcher() as fetcher:
        work = fetcher(rjcode)
        print(workinfo.work_filename(work))


if __name__ == '__main__':
    main()
