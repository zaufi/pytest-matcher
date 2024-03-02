.. SPDX-FileCopyrightText: 2017-now, See ``CONTRIBUTORS.lst``
.. SPDX-License-Identifier: CC0-1.0

What is this
============

|Latest Release| |nbsp| |Tests|

This is a ``pytest`` plugin provides a couple of fixtures to match test output against patterns
stored in files. Expectations/pattern files are stored in a base directory, and additional
paths are based on the test module name, test class name, and test function name::

    <base-dir>/<test-module-name>/[test-class-name/]<test-function-name>[[<callspec-id>]]

Note, that for non-class test functions, the *test-class-name* part is absent.
For parametrized tests, the *callspec-id* part containing %XX-escaped information
about the parametrization is added.

Having output expectations/pattern files separate from tests helps to reduce the code of the
latter and match the output more than just a few lines.


Documentation
-------------

The latest documentation could be found `here <https://pytest-matcher.readthedocs.io/en/latest/>`_.


See Also
========

* `How it works <http://zaufi.github.io/programming/2017/07/05/extend-pytest-with-fixtures>`_


.. |Latest Release| image:: https://img.shields.io/pypi/v/pytest-matcher
    :target: https://pypi.org/project/pytest-matcher/#history
    :alt: PyPI - Version

.. |Tests| image:: https://github.com/zaufi/pytest-matcher/actions/workflows/run-tests.yaml/badge.svg
    :target: https://github.com/zaufi/pytest-matcher/actions/workflows/run-tests.yaml
    :alt: Run Tests Result

.. |nbsp| unicode:: 0xA0
   :trim:
