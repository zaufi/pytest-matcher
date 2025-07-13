.. SPDX-FileCopyrightText: 2017-now, See ``CONTRIBUTORS.lst``
.. SPDX-License-Identifier: CC0-1.0

What is this
============

|Latest Release| |nbsp| |Tests|

This is a ``pytest`` plugin that provides a couple of fixtures to match test output against
patterns stored in files. Expectation files are placed in a base directory, and additional
paths are derived from the test module name, test class name and test function name::

    <base-dir>/<test-module-name>/[test-class-name/]<test-function-name>[[<callspec-id>]]

Keeping the expectation files separate from tests reduces the amount of test code and makes
it possible to match more than just a few lines of output.


Documentation
-------------

The latest documentation can be found `here <https://pytest-matcher.readthedocs.io>`_.


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
