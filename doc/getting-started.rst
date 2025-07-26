.. SPDX-FileCopyrightText: 2017-now, See ``CONTRIBUTORS.lst``
.. SPDX-License-Identifier: CC0-1.0

Getting Started
===============

.. program:: pytest-matcher

Install the package using the variant you want:

.. code-block:: console

    $ pip install pytest-matcher

or with ``diff`` mode highlighted via ``Pygments``:

.. code-block:: console

    $ pip install pytest-matcher[pygments]

The plugin provides the fixtures :py:data:`expected_out` and :py:data:`expected_err`.
Usage is straightforward as shown below:

.. literalinclude:: ../tests/test_foo.py
    :language: python
    :pyobject: test_foo

If you run :command:`pytest` now, the test will be skipped because the expectation file is missing:

.. code-block:: console
    :emphasize-lines: 5,6

    $ pytest --no-header --no-summary tests/test_foo.py::test_foo
    ============================= test session starts ==============================
    collected 1 item

    tests/test_foo.py::test_foo SKIPPED (Base directory for pattern-matcher
    does not exist: `…/pytest-matcher/master/tests/data/expected`)            [100%]

    ============================== 1 skipped in 0.01s ==============================


Add the :option:`pm-patterns-base-dir` option to the `Pytest configuration file`_
pointing, for example, to :file:`tests/data/expected`. Run :command:`pytest` with
the :option:`--pm-save-patterns` option to write the initial expectation file:

.. code-block:: console
    :emphasize-lines: 5,6

    $ pytest --pm-save-patterns --no-header --no-summary tests/test_foo.py::test_foo
    ============================= test session starts ==============================
    collecting ... collected 1 item

    tests/test_foo.py::test_foo SKIPPED (Pattern file saved to
    `…/pytest-matcher/master/tests/data/expected/test_foo/test_foo.out`)      [100%]

    ============================== 1 skipped in 0.02s ==============================

Review the stored pattern file :file:`tests/data/expected/test_foo/test_foo.out` and add it to
your VCS.

.. note::

    It’s recommended that you specify the exact test name(s) when writing the expectation file.
    Otherwise the plugin will overwrite all files, which is probably not what you want ;-)



Now that the expected output file exists, rerun :command:`pytest` to see that the test
output matches expectations:

.. code-block:: console
    :emphasize-lines: 5

    $ pytest --no-header --no-summary tests/test_foo.py::test_foo
    ============================= test session starts ==============================
    collected 1 item

    tests/test_foo.py::test_foo PASSED                                        [100%]

    ============================== 1 passed in 0.01s ===============================


.. _match-regex:

If the captured output contains values that change from run to run, for example timestamps
or filesystem paths, you can match the output using regular expressions:

.. literalinclude:: ../tests/test_foo.py
    :language: python
    :pyobject: test_regex

Store the pattern file for this test and rerun :command:`pytest` with the ``-vv`` option:

.. code-block:: console
    :emphasize-lines: 24,25,28,29

    $ pytest -vv --no-header tests/test_foo.py::test_regex
    ============================= test session starts ==============================
    collecting ... collected 1 item

    tests/test_foo.py::test_regex FAILED                                      [100%]

    =================================== FAILURES ===================================
    __________________________________ test_regex __________________________________

    capfd = <_pytest.capture.CaptureFixture object at 0x7f3a0e4a0110>
    expected_out = <matcher.plugin._ContentCheckOrStorePattern object at 0x7f3a0e4f2db0>

        def test_regex(capfd, expected_out):
            print(f"Current date: {datetime.now()}")
            print(f"Current module: {__file__}")

            stdout, _ = capfd.readouterr()

    >       assert expected_out.match(stdout) == True
    E       AssertionError: assert
    E         The test output doesn't match the expected regex.
    E         (from `…/pytest-matcher/master/tests/data/expected/test_foo/test_regex.out`):
    E         ---[BEGIN actual output]---
    E         Current date: 2024-03-02 21:59:03.792447
    E         Current module: …/pytest-matcher/master/tests/test_foo.py
    E         ---[END actual output]---
    E         ---[BEGIN expected regex]---
    E         Current date: 2024-03-02 21:58:32.289679
    E         Current module: …/pytest-matcher/master/tests/test_foo.py
    E         ---[END expected regex]---

    tests/test_foo.py:26: AssertionError
    =========================== short test summary info ============================
    FAILED tests/test_foo.py::test_regex - AssertionError: assert
    ============================== 1 failed in 0.03s ===============================

To make it match, edit the expectation file and replace the changing parts with regular
expressions:

.. code-block::
    :caption: ``tests/data/expect/test_foo/test_regex.out``

    Current date: [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?
    Current module: .*/tests/test_foo.py

The test will now pass:

.. code-block:: console
    :emphasize-lines: 5

    $ pytest --no-header --no-summary tests/test_foo.py::test_regex
    ============================= test session starts ==============================
    collected 1 item

    tests/test_foo.py::test_regex PASSED                                      [100%]

    ============================== 1 passed in 0.01s ===============================

The necessity to manually edit pattern after storing it (to make it a valid regular expression)
could be boring. With the :py:func:`on_store` marker, one can pass "instructions" on how to
edit raw text to turn it into a regular expression pattern.

.. literalinclude:: ../tests/test_foo.py
    :language: python
    :pyobject: test_on_store_marker
    :emphasize-lines: 1-7

So, now it's stored as a ready-to-match regex automatically:

.. code-block:: console
    :emphasize-lines: 12,13

    $ pytest --pm-save-patterns --no-header --no-summary tests/test_foo.py::test_on_store_marker
    ============================= test session starts ==============================
    collecting ... collected 1 item

    tests/test_foo.py::test_on_store_marker SKIPPED (Pattern file saved to
    `…/pytest-matcher/master/tests/data/expected/test_foo/test_on_store_m...) [100%]

    ============================== 1 skipped in 0.02s ==============================

    $ cat tests/data/expected/test_foo/test_on_store_marker.out
    The beginning of a static text that never changes from run to run\.
    Current date: [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?
    Current module: .*/tests/test_foo.py
    The text \*may have\* regex special\(\?\) metacharacters that \[would be\] escaped properly\.

    $ pytest --no-header --no-summary tests/test_foo.py::test_on_store_marker
    ============================= test session starts ==============================
    collected 1 item

    tests/test_foo.py::test_on_store_marker PASSED                            [100%]
    ============================== 1 passed in 0.01s ===============================


.. _Pytest configuration file: https://docs.pytest.org/en/latest/reference/customize.html
