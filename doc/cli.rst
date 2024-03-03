.. SPDX-FileCopyrightText: 2017-now, See ``CONTRIBUTORS.lst``
.. SPDX-License-Identifier: CC0-1.0

Plugin Command Line Options
===========================

.. program:: pytest-matcher

.. include:: include-traversal-warning.rst

.. option:: --pm-save-patterns

    Write the captured output to the expectations file instead of performing actual tests.
    The option helps collect initial content to match in further tests and skips the test.


.. option:: --pm-patterns-base-dir

    Specify the base directory to find expectation/pattern files.


.. option:: --pm-reveal-unused-files

    Reveal and print unused pattern files.  If :envvar:`PYTEST_MATCHER_RETURN_CODES` is
    set to the *true value* (one of ``1``, ``true``, ``yes``) and found any unused
    pattern files, the exit code will be ``1``.  The tests will not run.
