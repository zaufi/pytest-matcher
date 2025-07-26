.. SPDX-FileCopyrightText: 2017-now, See ``CONTRIBUTORS.lst``
.. SPDX-License-Identifier: CC0-1.0

Plugin Provided API
===================

.. program:: pytest-matcher

Fixture
-------

.. py:data:: expected_out
.. py:data:: expected_err

    This fixture makes it easy to test captured ``STDOUT`` and ``STDERR``.
    To match static output, simply use an ``assert``:

    .. code-block:: python

        def test_foo(capfd, expected_out, expected_err):
            ...
            stdout, stderr = capfd.readouterr()
            assert expected_out == stdout
            assert expected_stderr == stderr

    .. py:function:: expected_out.match(output: str) -> bool
    .. py:function:: expected_err.match(output: str) -> bool

        If the output contains data that changes from run to run (such as timestamps or paths),
        edit the expectation file to use regular expressions and match it with this function.
        See :ref:`Getting Started <match-regex>` for more details.

        .. code-block:: python
            :emphasize-lines: 4

            def test_foo(capfd, expected_out, expected_err):
                ...
                stdout, _ = capfd.readouterr()
                assert expected_out.match(stdout) == True

        .. note::
            The plugin provides detailed output on assertion failure, but it only works if you
            explicitly check for ``True`` from ``expected_out.match(…)``.

.. py:data:: expected_yaml

    This fixture provides an easy way to verify that YAML output matches the expectations.

    .. todo::
        More docs on this!


Marker
------

.. py:function:: expect_suffix(*args: str, suffix: str)

    If output may contain system-specific content (e.g., different EOL styles), you can add an
    arbitrary system-specific suffix to the pattern file so that different variants are stored in
    separate files.  Arguments to the marker are ``%XX``-escaped, dash-concatenated and prefixed with
    a leading ``-``. They are then used as the ``{suffix}`` placeholder of the
    :option:`pm-pattern-file-fmt` option.

    Usage example:

    .. code-block:: python

        @pytest.mark.expect_suffix(suffix=platform.system())
        def system_specific_test(capfd, expected_out):
            ...
            stdout, _ = capfd.readouterr()
            # Get content from `<base-dir>/.../system_specific_test-Linux.out`
            assert expected_out == stdout

        @pytest.mark.expect_suffix(
            f'py{sys.version_info.major}{sys.version_info.minor}'
          , f'pytest{pytest.version_tuple[0]}
          )
        def python_specific_test(capfd, expected_out):
            ...
            stdout, _ = capfd.readouterr()
            # Get content from `<base-dir>/.../python_specific_test-py312-pytest8.out`
            assert expected_out == stdout


.. py:function:: on_store(*, drop_head: int = 0, drop_tail: int = 0, replace_matched_lines: list[str] = [])

    Edit a pattern before save it when :option:`--pm-save-patterns` option has given.

    :param drop_head: Number of lines to remove from the beginning of the pattern. Removed lines are replaced
        with a ``.*`` placeholder to retain structural compatibility during pattern matching. The number must
        be a positive integer.
    :type x: int

    :param drop_tail: Number of lines to remove from the end of the pattern. The number must be a positive integer.
    :type x: int

    :param replace_matched_lines: A list of regular expression strings used to find and replace matching
        lines within the pattern.
    :type x: list[str]
