.. SPDX-FileCopyrightText: 2017-now, See ``CONTRIBUTORS.lst``
.. SPDX-License-Identifier: CC0-1.0

What is this
============

|Latest Release|

This is a ``pytest`` plugin that provides a couple of fixtures to match
test output against patterns stored in files.

Pattern files are stored in a base directory, and additional paths, based on the test
module name, test class name, and test function name, are as follows:

::

    <base-dir>/<test-module-name>/[test-class-name/]<test-function-name>[[<callspec-id>]]

Note, that for non-class test functions, the *test-class-name* part is absent.
For parametrized tests, the *callspec-id* part containing %XX-escaped information
about the parametrization is added.


Documentation
-------------

The latest documentation could be found `here <https://pytest-matcher.readthedocs.io/en/latest/>`_.


See Also
========

* `How it works <http://zaufi.github.io/programming/2017/07/05/extend-pytest-with-fixtures>`_

.. |Latest Release| image:: https://badge.fury.io/py/pytest-matcher.svg
    :target: https://pypi.org/project/pytest-matcher/#history
.. |nbsp| unicode:: 0xA0
   :trim:
