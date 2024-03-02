.. SPDX-FileCopyrightText: 2017-now, See ``CONTRIBUTORS.lst``
.. SPDX-License-Identifier: CC0-1.0

==========
Change Log
==========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog`_ and this project adheres
to `Semantic Versioning`_.

.. _Keep a Changelog: http://keepachangelog.com/
.. _Semantic Versioning: http://semver.org/

Unreleased_
===========

Added
-----
- Introduce ``pm-pattern-file-fmt`` configuration parameter to give full
  control over the path to pattern files.
- A test can be marked with ``@pytest.mark.expect_suffix([args..., suffix=<arg>])``
  to have an arbitrary suffix in the pattern filenames.
  The ``pm-pattern-file-fmt`` format string should have the ``{suffix}`` placeholder
  to make it work. See issue #22.

Fixed
-----

- **BREAKING CHANGE** The expectation files path has never used the
  ``<test-module-name>`` component despite the ``README.rst`` claimed.
  Existed projects could set ``pm-pattern-file-fmt`` to
  ``{class}/{fn}{callspec}`` to preserve backward compatibility.

Removed
-------

- **BREAKING CHANGE** The ``pm-pattern-file-use-system-name`` configuration
  parameter has been removed. Having ``{suffix}`` in the ``pm-pattern-file-fmt``
  one can have a system name suffix whenever he needs it.


1.6.0_ -- 2024-02-29
====================

Added
-----

- ``--pm-reveal-unused-files`` option to reveal unused pattern files.
- run test with ``pytest`` 7.x and 8.x.


1.5.1_ -- 2024-01-15
====================

Fixed
-----

- Regression with Python less than 3.11.

1.5.0_ -- 2024-01-11
====================

Added
-----

- [4_] Make it possible to use ``expected_xxx`` with parameterized tests.


1.4.0_ -- 2021-12-10
====================

Added
-----

- Allow ``assert expected_out.match(blah_blah) is True``.

Changed
-------

- Migrate to ``setup.py``-less build (using PEP517 and PEP660).


1.3.3_ -- 2019-06-27
====================

Fixed
-----

- Fix backward compatibility w/ Python less than 3.6.


1.3.2_ -- 2019-06-26
====================

Fixed
-----

- When a caller use ``re.MULTILINE`` the plugin do not use ``splitlines``.


1.3.1_ -- 2019-04-04
====================

Added
-----

- Show actual and expected output on failed ``expected_out.match()``.


1.2.2_ -- 2019-04-04
====================

Fixed
-----

- Update code for modern ``pytest`` (4.4.0) and ``PyYAML`` (5.1).


1.2.1_ -- 2018-03-30
====================

Fixed
-----

- Update meta-data of the project for PyPi.


1.2.0_ -- 2018-03-30
====================

Added
-----

- Add an INI-file option ``pm-pattern-file-use-system-name`` to control if the system
  name suffix is expected to be in a pattern filename. E.g. this allows having patterns with
  different CR/LF conventions;
- Add ``expected_yaml`` fixture to match YAML files;
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

- Ensure full pattern match for ``expected_xxx.match()`` named fixtures.


1.0.0_ -- 2017-08-25
====================

Added
-----

- Add pretty printer for failed asserts with ``expected_out`` fixture and equal comparison operator.


.. _Unreleased: https://github.com/zaufi/pytest-matcher/compare/release/1.6.0...HEAD
.. _1.6.0: https://github.com/zaufi/pytest-matcher/compare/release/1.5.1...release/1.6.0
.. _1.5.1: https://github.com/zaufi/pytest-matcher/compare/release/1.5.0...release/1.5.1
.. _1.5.0: https://github.com/zaufi/pytest-matcher/compare/release/1.4.0...release/1.5.0
.. _1.4.0: https://github.com/zaufi/pytest-matcher/compare/release/1.3.3...release/1.4.0
.. _1.3.3: https://github.com/zaufi/pytest-matcher/compare/release/1.3.2...release/1.3.3
.. _1.3.2: https://github.com/zaufi/pytest-matcher/compare/release/1.3.1...release/1.3.2
.. _1.3.1: https://github.com/zaufi/pytest-matcher/compare/release/1.2.2...release/1.3.1
.. _1.2.2: https://github.com/zaufi/pytest-matcher/compare/release/1.2.1...release/1.2.2
.. _1.2.1: https://github.com/zaufi/pytest-matcher/compare/release/1.2.0...release/1.2.1
.. _1.2.0: https://github.com/zaufi/pytest-matcher/compare/release/1.1.0...release/1.2.0
.. _1.1.0: https://github.com/zaufi/pytest-matcher/compare/release/1.0.0...release/1.1.0
.. _1.0.0: https://github.com/zaufi/pytest-matcher/compare/release/0.9.0...release/1.0.0
.. _4: https://github.com/zaufi/pytest-matcher/issues/4
