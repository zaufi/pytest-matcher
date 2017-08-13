What is this
============

This is a pytest plugin which provides a could of fixtures to match
test output against patterns stored in files.

The plugin extend pytest with the following CLI options:

- ``--pm-save-patterns`` -- to store output to a pattern file (instead of checking);
- ``--pm-patterns-base-dir`` to specify a base directory, where to lookup pattern files.

Pattern files are stored in a base directory and additional paths based on test module
name, test class name and/or test function name as following:

::

    <base-dir>/<test-module-name>/[test-class-name]/<test-function-name>

Note, that for non-class test functions the *class-name* part is absent.


Quick Start
===========

The plugin provides :py:function:`expected_out` and :py:function:`expected_err`
named fixture functions.


.. code-block:: python

    def test_foo(capfd, expected_out):
        print('foo')

        stdout, stderr = capfd.readouterr()

        assert stdout == expected_out

For the first ``pytest`` run it would fail, cuz there is no expected pattern file present.
To write, it one can use :command:`pytest` CLI:

::

    $ pytest --pm-save-patterns test/test_foo.py::test_foo

Review the stored pattern file and add to your VCS.


See Also
========

* `How it works <http://zaufi.github.io/programming/2017/07/05/extend-pytest-with-fixtures>`_
