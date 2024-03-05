.. SPDX-FileCopyrightText: 2017-now, See ``CONTRIBUTORS.lst``
.. SPDX-License-Identifier: CC0-1.0

Plugin Provided API
===================

.. program:: pytest-matcher

Fixture
-------

.. py:data:: expected_out
.. py:data:: expected_err

    This fixture provides an easy way to test captured ``STDOUT``/``STDERR``.
    To match a static output, one can use a trivial ``assert``:

    .. code-block:: python

        def test_foo(capfd, expected_out, expected_err):
            ...
            stdout, stderr = capfd.readouterr()
            assert expected_out == stdout
            assert expected_stderr == stderr

    .. py:function:: expected_out.match(output: str) -> bool
    .. py:function:: expected_err.match(output: str) -> bool

        If the output has data changed from run to run (like timestamps or paths), one can edit the
        expected output file using regular expressions and use this function to match them.
        Please see :ref:`Getting Started <match-regex>` for more information about this topic.

        .. code-block:: python
            :emphasize-lines: 4

            def test_foo(capfd, expected_out, expected_err):
                ...
                stdout, _ = capfd.readouterr()
                assert expected_out.match(stdout) == True

        .. note::
            The plugin provides elaborate output on assert failure, but to make it work, one
            should use an explicit check for the ``True`` value of the ``expected_out.match(…)``
            result.

.. py:data:: expected_yaml

    This fixture provides an easy way to check if the output YAML data matches
    the expectations.

    .. todo::
        More docs on this!


Marker
------

.. py:function:: expect_suffix(*args: str, suffix: str)

    If output may have system-specific content (e.g., different EOL styles), adding an arbitrary
    system-specific suffix to the pattern file makes storing different variants in separate files
    possible.  Arguments to the marker will be ``%XX``-escaped, dash-concatenated and prefixed with
    leading ``-`` and then used as the ``{suffix}`` placeholder of the :option:`pm-pattern-file-fmt`
    option.

    Usage example:

    .. code-block:: python

        @pytest.mark.expect_suffix(suffix=platform.system())
        def system_specific_test(capfd, expected_out):
            ...
            stdout, _ = capfd.readouterr()
            # Get content from `<base-dir>/.../system_specific-Linux.out`
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
