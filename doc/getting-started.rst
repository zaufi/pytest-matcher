.. SPDX-FileCopyrightText: 2017-now, See ``CONTRIBUTORS.lst``
.. SPDX-License-Identifier: CC0-1.0

Getting Started
===============

.. program:: pytest-matcher

Install the package in the variant you want:

.. code-block:: console

    $ pip install pytest-matcher

or with ``diff`` mode highlighted with ``Pygments``:

.. code-block:: console

    $ pip install pytest-matcher[pygments]

The plugin provides :py:data:`expected_out` and :py:data:`expected_err` named fixture functions.
The usage is trivial as the following:

.. literalinclude:: ../test/test_foo.py
    :language: python
    :pyobject: test_foo

If you run :command:`pytest` now, it'll skip the test due to a missed output expectations file:

.. code-block:: console
    :emphasize-lines: 5,6

    $ pytest --no-header --no-summary test/test_foo.py::test_foo
    ============================= test session starts ==============================
    collected 1 item

    test/test_foo.py::test_foo SKIPPED (Base directory for pattern-matcher
    do not exists: `…/pytest-matcher/master/test/data/expected`)               [100%]

    ============================== 1 skipped in 0.01s ==============================


Add the :option:`pm-patterns-base-dir` option to the `Pytest configuration file`_
pointing, for example, to :file:`test/data/expected`.  Add the :option:`--pm-save-patterns`
:command:`pytest` CLI option to write the initial output expectations file:

.. code-block:: console
    :emphasize-lines: 5,6

    $ pytest --pm-save-patterns --no-header --no-summary test/test_foo.py::test_foo
    ============================= test session starts ==============================
    collecting ... collected 1 item

    test/test_foo.py::test_foo SKIPPED (Pattern file has been saved
    `…/pytest-matcher/master/test/data/expected/test_foo/test_foo.out`)       [100%]

    ============================== 1 skipped in 0.02s ==============================

Review the stored pattern file :file:`test/data/expected/test_foo/test_foo.out` and add it to your VCS.

.. note::

    It’s recommended that the exact test name(s) be specified when writing the expectations file.
    Otherwise, the plugin will overwrite all files that are most likely not what you want ;-)



Now, when the expected output file exists, you can rerun :command:`pytest` to see that the test output
is matching expectations:

.. code-block:: console
    :emphasize-lines: 5

    $ pytest --no-header --no-summary test/test_foo.py::test_foo
    ============================= test session starts ==============================
    collected 1 item

    test/test_foo.py::test_foo PASSED                                        [100%]

    ============================== 1 passed in 0.01s ===============================


.. _match-regex:

If the captured output has something that could change from run to run, for example, timestamps
or filesystem paths, it's possible to match the output using regular expressions:

.. literalinclude:: ../test/test_foo.py
    :language: python
    :pyobject: test_regex

Store the pattern file for this test and rerun :command:`pytest` with ``-vv`` option:

.. code-block:: console
    :emphasize-lines: 24,28

    $ pytest -vv --no-header test/test_foo.py::test_regex
    ============================= test session starts ==============================
    collecting ... collected 1 item

    test/test_foo.py::test_regex FAILED                                      [100%]

    =================================== FAILURES ===================================
    __________________________________ test_regex __________________________________

    capfd = <_pytest.capture.CaptureFixture object at 0x7f3a0e4a0110>
    expected_out = <matcher.plugin._ContentCheckOrStorePattern object at 0x7f3a0e4f2db0>

        def test_regex(capfd, expected_out):
            print(f"Current date: {datetime.now()}")
            print(f"Current module: {__file__}")

            stdout, _ = capfd.readouterr()

    >       assert expected_out.match(stdout) ==True
    E       AssertionError: assert
    E         The test output doesn't match to the expected regex
    E         (from `…/pytest-matcher/master/test/data/expected/test_foo/test_regex.out`):
    E         ---[BEGIN actual output]---
    E         Current date: 2024-03-02 21:59:03.792447
    E         Current module: …/pytest-matcher/master/test/test_foo.py
    E         ---[END actual output]---
    E         ---[BEGIN expected regex]---
    E         Current date: 2024-03-02 21:58:32.289679
    E         Current module: …/pytest-matcher/master/test/test_foo.py
    E         ---[END expected regex]---

    test/test_foo.py:26: AssertionError
    =========================== short test summary info ============================
    FAILED test/test_foo.py::test_regex - AssertionError: assert
    ============================== 1 failed in 0.03s ===============================

To make it match, edit the expected output file and replace changing parts with regular
expressions:

.. code-block::
    :caption: ``test/data/expect/test_foo/test_regex.out``

    Current date: [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?
    Current module: .*/test/test_foo.py

Now the test will pass:

.. code-block:: console
    :emphasize-lines: 5

    $ pytest --no-header --no-summary test/test_foo.py::test_regex
    ============================= test session starts ==============================
    collected 1 item

    test/test_foo.py::test_regex PASSED                                        [100%]

    ============================== 1 passed in 0.01s ===============================

.. _Pytest configuration file: https://docs.pytest.org/en/8.0.x/reference/customize.html
