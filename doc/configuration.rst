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

    When the expected output does not match, this option controls how the failure is reported:

    - ``full`` -- show actual and expected output separately (default).
    - ``diff`` -- show a unified diff between actual and expected text.


.. option:: pm-pattern-file-fmt

    :Default: ``{module}/{class}/{fn}{callspec}{suffix}``

    Expectation filename pattern. It can contain the following placeholders:

    - ``{module}`` for the test module name.
    - ``{class}`` for the test class name.
    - ``{fn}`` for the test function name.
    - ``{callspec}`` for the parameterized part of the test function.
    - ``{suffix}`` for the optional suffix added by the :py:func:`expect_suffix` mark.

    Note that for non-class test functions, the ``{class}`` placeholder will be empty.
    For parametrized tests, the ``{callspec}`` placeholder contains ``%XX``-escaped information
    about the parametrization.


.. option:: pm-patterns-base-dir

    :Default: :file:`tests/data/expected`

    Base directory used for storing pattern files.
    The directory must be relative to the project's root.


.. _Pytest configuration file: https://docs.pytest.org/en/latest/reference/customize.html
