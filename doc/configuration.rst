.. SPDX-FileCopyrightText: 2017-now, See ``CONTRIBUTORS.lst``
.. SPDX-License-Identifier: CC0-1.0

Plugin Configuration Options
============================

.. program:: pytest-matcher

.. include:: include-traversal-warning.rst

The following options can be set in the `Pytest configuration file`_.

.. option:: pm-mismatch-style

    :Choice: ``full``, ``diff``
    :Default: ``full``

    In case of expected output mismatch, specifies how to report a test failure:

    - ``full`` -- shows actual and expected separately (default).
    - ``diff`` -- shows a unified diff between actual and expected text.


.. option:: pm-pattern-file-fmt

    :Default: ``{module}/{class}/{fn}{callspec}{suffix}``

    Expectations filename pattern format. It can have the following placeholders:

    - ``{module}`` for the test module name.
    - ``{class}`` for the test class name.
    - ``{fn}`` for the test function name.
    - ``{callspec}`` for the parameterized part of the test function.
    - ``{suffix}`` for the optional suffix added by the :py:func:`expect_suffix` mark.

    Note that for non-class test functions, the ``{class}`` placeholder part will be empty.
    For parametrized tests, the ``{callspec}`` placeholder containing ``%XX``-escaped information
    about the parametrization is added.


.. option:: pm-patterns-base-dir

    :Default: :file:`test/data/expected`

    The base directory is used to place expectations/pattern files.
    Given directory must be relative to the project's root.


.. _Pytest configuration file: https://docs.pytest.org/en/8.0.x/reference/customize.html
