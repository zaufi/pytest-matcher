.. SPDX-FileCopyrightText: 2017-now, See ``CONTRIBUTORS.lst``
.. SPDX-License-Identifier: CC0-1.0

What is this
============

|Latest Release|

This is a pytest plugin which provides a couple of fixtures to match
test output against patterns stored in files.

The plugin extends pytest with the following CLI options:

- ``--pm-save-patterns`` -- to store the output to a pattern file (instead of checking);
- ``--pm-patterns-base-dir`` to specify a base directory, where to lookup pattern files.

Pattern files are stored in a base directory and additional paths based on test module
name, test class name and/or test function name as following:

::

    <base-dir>/<test-module-name>/[test-class-name/]<test-function-name>[[<callspec-id>]]

Note, that for non-class test functions the *test-class-name* part is absent.
For parametrized tests, the *callspec-id* part containing %XX-escaped information
about the parametrization is added.


Quick Start
===========

The plugin provides ``expected_out`` and ``expected_err``
named fixture functions.


.. code-block:: python

    def test_foo(capfd, expected_out):
        print('foo')

        stdout, stderr = capfd.readouterr()

        assert stdout == expected_out

Add ``pm-patterns-base-dir`` option to ``pytest.ini`` file (and ``pytest`` section)
pointing for example to ``test/data/expected``. For the first ``pytest`` run it would
fail, cuz there is no expected pattern file present. To write it one can use
``pytest`` CLI:

::

    $ pytest --pm-save-patterns test/test_foo.py::test_foo

Review the stored pattern file and add to your VCS.


See Also
========

* `How it works <http://zaufi.github.io/programming/2017/07/05/extend-pytest-with-fixtures>`_

.. |Latest Release| image:: https://badge.fury.io/py/pytest-matcher.svg
    :target: https://pypi.org/project/pytest-matcher/#history
.. |nbsp| unicode:: 0xA0
   :trim:
