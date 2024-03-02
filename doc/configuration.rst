.. SPDX-FileCopyrightText: 2017-now, See ``CONTRIBUTORS.lst``
.. SPDX-License-Identifier: CC0-1.0

Plugin Configuration Options
============================

.. program:: pytest-matcher


The following options can be set in the `Pytest configuration file`_.

.. option:: pm-patterns-base-dir

    The base directory is used to place expectations/pattern files.


.. option:: pm-pattern-file-fmt

    Expectations filename pattern format. It can have the following placeholders:

    - ``{module}`` for the test module name.
    - ``{class}`` for the test class name.
    - ``{fn}`` for the test function name.
    - ``{callspec}`` for the parameterized part of the test function.
    - ``{suffix}`` for the optional suffix added by the :py:func:`expect_suffix` mark.

    The default value is::

        {module}/{class}/{fn}{callspec}{suffix}


.. include:: include-traversal-warning.rst

.. _Pytest configuration file: https://docs.pytest.org/en/8.0.x/reference/customize.html
