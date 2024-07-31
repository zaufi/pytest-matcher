.. SPDX-FileCopyrightText: 2017-now, See ``CONTRIBUTORS.lst``
.. SPDX-License-Identifier: CC0-1.0

Plugin Command Line Options
===========================

.. program:: pytest-matcher

.. include:: include-traversal-warning.rst

.. option:: --pm-mismatch-style <diff|full>

    Overrides the value of :option:`pm-mismatch-style` configuration parameter.


.. option:: --pm-patterns-base-dir <DIR>

    Specify the base directory to find expectation/pattern files.
    See also :option:`pm-patterns-base-dir`.


.. option:: --pm-reveal-unused-files

    Reveal and print unused pattern files.  If :envvar:`PYTEST_MATCHER_RETURN_CODES`
    environment variable is set to the *true value* (one of ``1``, ``true``, ``yes``)
    and found any unused pattern files, the exit code will be ``1``.
    The tests will not run.


.. option:: --pm-save-patterns

    Write the captured output to the expectations file instead of performing actual tests.
    The option helps collect initial content to match in further tests and skips the test.
