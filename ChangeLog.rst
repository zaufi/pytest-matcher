.. SPDX-FileCopyrightText: 2017-now, See ``CONTRIBUTORS.lst``
.. SPDX-License-Identifier: CC0-1.0

==========
Change Log
==========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog`_ and this project adheres
to `Semantic Versioning`_.

.. _Keep a Changelog: https://keepachangelog.com/
.. _Semantic Versioning: https://semver.org/

.. Types of changes (https://keepachangelog.com/en/1.1.0/#types)
..   ✔ ``Added`` for new features.
..   ✔ ``Changed`` for changes in existing functionality.
..   ✔ ``Deprecated`` for soon-to-be removed features.
..   ✔ ``Removed`` for now removed features.
..   ✔ ``Fixed`` for any bug fixes.
..   ✔ ``Security`` in case of vulnerabilities.

.. program:: pytest-matcher

2.1.0_ -- 2025-08-08
====================

Added
-----

- Automate pattern editing (preparation) with the :py:func:`on_store` marker.
- Make the :py:data:`expected_out` printable.

Fixed
-----

- Updated the default value of :option:`pm-pattern-file-fmt` to append ``{suffix}``,
  which was missing despite being documented.


2.0.3_ -- 2025-07-26
====================

Changed
-------

- Set the :option:`pm-patterns-base-dir` default to :file:`tests/data/expected` to align with
  the common :file:`tests/` directory layout.
- Improve documentation.
- Update the :file:`pyproject.toml` to suit the :program:`hatch test` command.

Fixed
-----

- Handle invalid values of the :option:`pm-pattern-file-fmt` option.


2.0.2_ -- 2024-08-01
====================

Changed
-------

- **BREAKING CHANGE** Remove Python 3.9 from classifiers (ought to be done in 1.6.0).
- Little improvements in documentation.


2.0.1_ -- 2024-03-15
====================

Added
-----

- Quick check for the :file:`ChangeLog.rst`.

Fixed
-----

- The release GitHub workflow has been updated to use modern versions of the involved actions.
- Do not override the path suffix-like part (separated by a dot) with a pattern
  filename extension.


2.0.0_ -- 2024-03-11
====================

Added
-----
- Introduce :option:`pm-pattern-file-fmt` configuration parameter to give full
  control over the path to pattern files.
- A test can be marked with :py:func:`@pytest.mark.expect_suffix <expect_suffix>`
  to have an arbitrary suffix in the pattern filenames.
  The :option:`pm-pattern-file-fmt` format string should have the ``{suffix}`` placeholder
  to make it work. See :issue:`22`.
- `Documentation`_.
- Introduce :option:`pm-mismatch-style`.
- Show newlines in the ``full`` mismatch mode.

Fixed
-----

- **BREAKING CHANGE** The expectation files path has never used the
  ``<test-module-name>`` component despite the :file:`README.rst` claimed.
  Existing projects could set :option:`pm-pattern-file-fmt` to
  ``{class}/{fn}{callspec}`` to preserve backward compatibility.

Removed
-------

- **BREAKING CHANGE** The :option:`!pm-pattern-file-use-system-name` configuration
  parameter has been removed. Having ``{suffix}`` in the :option:`pm-pattern-file-fmt`
  one can have a system name suffix whenever he needs it.


1.6.0_ -- 2024-02-29
====================

Added
-----

- :option:`--pm-reveal-unused-files` option to reveal unused pattern files.
- run test with :command:`pytest` 7.x and 8.x.


1.5.1_ -- 2024-01-15
====================

Fixed
-----

- Regression with Python less than 3.11.

1.5.0_ -- 2024-01-11
====================

Added
-----

- Make it possible to use :py:data:`expected_xxx <expected_out>` with parameterized tests. See :issue:`4`.


1.4.0_ -- 2021-12-10
====================

Added
-----

- Allow ``assert expected_out.match(blah_blah) is True``.

Changed
-------

- Migrate to :file:`setup.py`-less build (using :pep:`517` and :pep:`660`).


1.3.3_ -- 2019-06-27
====================

Fixed
-----

- Fix backward compatibility with Python less than 3.6.


1.3.2_ -- 2019-06-26
====================

Fixed
-----

- When a caller uses ``re.MULTILINE``, the plugin does not use ``splitlines``.


1.3.1_ -- 2019-04-04
====================

Added
-----

- Show actual and expected output on failed :py:func:`expected_out.match()`.

Changed
-------

- Update code for the modern ``pytest`` (4.4.0) and ``PyYAML`` (5.1).


1.2.1_ -- 2018-03-30
====================

Fixed
-----

- Update meta-data of the project for PyPi.


1.2.0_ -- 2018-03-30
====================

Added
-----

- Add an INI-file option :option:`!pm-pattern-file-use-system-name` to control if the system
  name suffix is expected to be in a pattern filename. For example, this allows patterns with
  different CR/LF conventions to be created.
- Add :py:data:`expected_yaml` fixture to match YAML files.
- Introduce unit tests.


1.1.0_ -- 2018-03-28
====================

Added
-----

- Use ``pytest.skip()`` if no pattern file has been found or it contains an invalid
  regular expression;
- Added doc-strings to the fixtures, so :command:`pytest --fixtures` would not complain.

Changed
-------

- Ensure full pattern match for :py:func:`expected_xxx.match <expected_out.match>` named fixtures.


1.0.0_ -- 2017-08-25
====================

Added
-----

- Add a pretty printer for failed assertions with the :py:data:`expected_out` fixture and equal
  comparison operator.


.. _Unreleased: https://github.com/zaufi/pytest-matcher/compare/release/2.1.0...HEAD
.. _2.1.0: https://github.com/zaufi/pytest-matcher/compare/release/2.0.3...release/2.1.0
.. _2.0.3: https://github.com/zaufi/pytest-matcher/compare/release/2.0.2...release/2.0.3
.. _2.0.2: https://github.com/zaufi/pytest-matcher/compare/release/2.0.1...release/2.0.2
.. _2.0.1: https://github.com/zaufi/pytest-matcher/compare/release/2.0.0...release/2.0.1
.. _2.0.0: https://github.com/zaufi/pytest-matcher/compare/release/1.6.0...release/2.0.0
.. _1.6.0: https://github.com/zaufi/pytest-matcher/compare/release/1.5.1...release/1.6.0
.. _1.5.1: https://github.com/zaufi/pytest-matcher/compare/release/1.5.0...release/1.5.1
.. _1.5.0: https://github.com/zaufi/pytest-matcher/compare/release/1.4.0...release/1.5.0
.. _1.4.0: https://github.com/zaufi/pytest-matcher/compare/release/1.3.3...release/1.4.0
.. _1.3.3: https://github.com/zaufi/pytest-matcher/compare/release/1.3.2...release/1.3.3
.. _1.3.2: https://github.com/zaufi/pytest-matcher/compare/release/1.3.1...release/1.3.2
.. _1.3.1: https://github.com/zaufi/pytest-matcher/compare/release/1.2.1...release/1.3.1
.. _1.2.1: https://github.com/zaufi/pytest-matcher/compare/release/1.2.0...release/1.2.1
.. _1.2.0: https://github.com/zaufi/pytest-matcher/compare/release/1.1.0...release/1.2.0
.. _1.1.0: https://github.com/zaufi/pytest-matcher/compare/release/1.0.0...release/1.1.0
.. _1.0.0: https://github.com/zaufi/pytest-matcher/compare/release/0.9.0...release/1.0.0
.. _Documentation: https://pytest-matcher.readthedocs.io/latest/index.html
