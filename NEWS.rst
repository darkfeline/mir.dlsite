mir.dlsite Release Notes
========================

This project uses `semantic versioning <http://semver.org/>`_.

0.8.0
-----

Added
^^^^^

- Added genre support.

0.7.0 (2020-10-15)
------------------

Fixed
^^^^^

- Fixed parsing new DLSite page format.

0.6.0 (2019-10-25)
------------------

Changed
^^^^^^^

- Use HTTPS instead of HTTP for accessing DLSite.

0.5.0 (2018-05-22)
------------------

Changed
^^^^^^^

- `dlorg` now handles each work sequentially rather than in batch.
  This primarily affects what happens if a duplicate work is
  encountered and `-d` is used.

Removed
^^^^^^^

- `org` module removed (it wasn't really a good public API anyway).

0.4.0 (2017-11-05)
------------------

Added
^^^^^

- Added tracklist support.
- Added description support.

Changed
^^^^^^^

- Renamed `mir.scripts` to `mir.cmd`.
- API rejiggered.

0.3.0 (2017-10-05)
------------------

Added
^^^^^

- Added `--all` option to `dlorg` allow for faster shallow runs.

Changed
^^^^^^^

- Renamed `rj.contains` to `rj.inside`.

0.2.0 (2017-07-30)
------------------

Added
^^^^^

- Caching of dlsite data.

0.1.0 (2016-09-11)
------------------

Initial release.
