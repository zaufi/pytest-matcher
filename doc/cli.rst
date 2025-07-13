.. SPDX-FileCopyrightText: 2017-now, See ``CONTRIBUTORS.lst``
.. SPDX-License-Identifier: CC0-1.0

Plugin Command Line Options
===========================

.. program:: pytest-matcher

.. include:: include-traversal-warning.rst

.. option:: --pm-mismatch-style <diff|full>

    Override the value of the :option:`pm-mismatch-style` configuration parameter.


.. option:: --pm-patterns-base-dir <DIR>

    Specify the base directory used to find expectation/pattern files.
    See also :option:`pm-patterns-base-dir`.


.. option:: --pm-reveal-unused-files

    Reveal and print unused pattern files. If the environment variable
    :envvar:`PYTEST_MATCHER_RETURN_CODES` is set to a true value (one of ``1``,
    ``true``, ``yes``) and any unused pattern files are found, the exit code will be ``1``.
    Tests will not run.


.. option:: --pm-save-patterns

    Write the captured output to the expectation file instead of performing the test.
    This option helps collect the initial pattern and skips the test.
