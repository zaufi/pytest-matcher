#
# SPDX-FileCopyrightText: 2017-now, See `CONTRIBUTORS.lst`
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""A `pytest` plugin to match test output against expectations."""

from __future__ import annotations

# Standard imports
import pathlib
import platform
import re
import shutil
import sys
import urllib.parse
from typing import Final, cast

# Third party packages
import pytest
import yaml

if sys.version_info < (3, 11):
    _RE_NOFLAG: Final[re.RegexFlag] = cast(re.RegexFlag, 0)
else:
    _RE_NOFLAG: Final[re.RegexFlag] = re.NOFLAG


class _content_match_result:
    """TODO Is this job for Python `dataclass`?"""

    def __init__(self, result: bool, text: list[str], regex: str, filename: pathlib.Path) -> None:  # NOQA: FBT001
        self._result = result
        self._text = text
        self._regex = regex
        self._filename = filename

    def __eq__(self, other: object) -> bool:
        if isinstance(other, bool):
            return self._result == other
        return False

    def __bool__(self) -> bool:
        return self._result

    def report_regex_mismatch(self) -> list[str]:
        return [
            ''
          , "The test output doesn't match to the expected regex"
          , f'(from `{self._filename}`):'
          , '---[BEGIN actual output]---'
          , *self._text
          , '---[END actual output]---'
          , '---[BEGIN expected regex]---'
          , *self._regex.splitlines()
          , '---[END expected regex]---'
          ]


class _content_check_or_store_pattern:

    def __init__(self, filename: pathlib.Path, *, store: bool) -> None:
        self._pattern_filename = filename
        self._store = store
        self._expected_file_content: str | None = None

    @staticmethod
    def _store_pattern_handle_error(fn):
        def _inner(self, text, *args, **kwargs):
            # Check if `--save-patterns` has given to CLI
            if self._store:
                # Make a directory to store a pattern file if it doesn't exist yet
                if not self._pattern_filename.parent.exists():
                    self._pattern_filename.parent.mkdir(parents=True)

                assert self._pattern_filename.parent.is_dir()

                # Store!
                self._pattern_filename.write_text(text)

                return True

            # Ok, this is the "normal" check:
            # - make sure the pattern file exists
            if not self._pattern_filename.exists() or self._pattern_filename.is_dir():
                pytest.skip(f'Pattern file not found `{self._pattern_filename}`')

            # - call wrapped function to
            return fn(self, text, *args, **kwargs)

        return _inner

    def _read_expected_file_content(self):
        self._expected_file_content = self._pattern_filename.read_text()

    @_store_pattern_handle_error
    def __eq__(self, text: str) -> bool:
        self._read_expected_file_content()
        return self._expected_file_content == text

    @_store_pattern_handle_error
    def match(self, text: str, flags: re.RegexFlag = _RE_NOFLAG) -> _content_match_result:
        self._read_expected_file_content()
        content = (
            '.*\n' if flags & re.MULTILINE else ' '
          ).join(
              self._expected_file_content.strip().splitlines()  # type: ignore[union-attr]
            )
        try:
            if flags & re.MULTILINE:
                what = re.compile('.*' + content + '.*', flags=flags)
            else:
                what = re.compile(content, flags=flags)

        except re.error as ex:
            pytest.skip(f'Compile a regular expression from the pattern has failed: {ex!s}')

        text_lines = text.splitlines()

        m = what.fullmatch(('\n' if flags & re.MULTILINE else ' ').join(text_lines))
        return _content_match_result(
            m is not None and bool(m)
          , text_lines
          , self._expected_file_content                     # type: ignore[arg-type]
          , self._pattern_filename
          )

    def report_compare_mismatch(self, actual: str) -> list[str]:
        assert self._expected_file_content is not None
        return [
            ''
          , "The test output doesn't equal to the expected"
          , f'(from `{self._pattern_filename}`):'
          , '---[BEGIN actual output]---'
          , *actual.splitlines()
          , '---[END actual output]---'
          , '---[BEGIN expected output]---'
          , *self._expected_file_content.splitlines()
          , '---[END expected output]---'
          ]


def _try_cli_option(request) -> tuple[pathlib.Path | None, bool]:
    result = request.config.getoption('--pm-patterns-base-dir')
    return (pathlib.Path(result) if result is not None else None, True)


def _try_ini_option(request) -> tuple[pathlib.Path | None, bool]:
    result = request.config.getini('pm-patterns-base-dir')
    return (pathlib.Path(result) if result else None, False)


def _try_module_path(request) -> tuple[pathlib.Path, bool]:
    assert request.fspath.dirname is not None
    # NOTE Suppose the current test module's directory has `data/expected/` inside
    return (pathlib.Path(request.fspath.dirname) / 'data' / 'expected', False)


def _make_expected_filename(request, ext: str, *, use_system_suffix=True) -> pathlib.Path:
    result: pathlib.Path | None = None
    use_cwd_as_base = False
    for alg in [_try_cli_option, _try_ini_option, _try_module_path]:
        result, use_cwd_as_base = alg(request)
        if result is not None:
            break

    assert result is not None

    if use_system_suffix:
        use_system_suffix = request.config.getini('pm-pattern-file-use-system-name')
        use_system_suffix = use_system_suffix in ('true', '1')

    # Make the found path absolute using pytest's rootdir as the base
    if not result.is_absolute():
        if use_cwd_as_base:
            result = pathlib.Path.cwd()
        elif request.config.inifile is not None:
            result = pathlib.Path(request.config.inifile.dirname) / result
        else:
            # TODO Better error description.
            pytest.fail('Unable to determine the path to expectation files')

    # Make sure base directory exists
    if not result.exists():
        pytest.skip(f'Base directory for pattern-matcher do not exists: `{result}`')

    if request.cls is not None:
        result /= request.cls.__name__

    result /= (                                             # type: ignore[operator]
        urllib.parse.quote(request.node.name, safe='[]')
      + ('-' + platform.system() if use_system_suffix else '')
      + ext
      )

    return result


@pytest.fixture()
def expected_out(request):
    """A pytest fixture to match `STDOUT` against a file."""
    return _content_check_or_store_pattern(
        _make_expected_filename(request, '.out')
      , store=request.config.getoption('--pm-save-patterns')
      )


@pytest.fixture()
def expected_err(request):
    """A pytest fixture to match `STDERR` against a file."""
    return _content_check_or_store_pattern(
        _make_expected_filename(request, '.err')
      , store=request.config.getoption('--pm-save-patterns')
      )


class _yaml_check_or_store_pattern:

    def __init__(self, filename: pathlib.Path, *, store: bool) -> None:
        self._expected_file = filename
        self._store = store


    def _store_pattern_file(self, result_file: pathlib.Path) -> None:
        assert self._store, 'Code review required!'

        if not self._expected_file.parent.exists():
            self._expected_file.parent.mkdir(parents=True)

        assert self._expected_file.parent.is_dir()

        shutil.copy(str(result_file), str(self._expected_file))



    def __eq__(self, result_file: object) -> bool:
        assert isinstance(result_file, pathlib.Path)

        if self._store:
            self._store_pattern_file(result_file)
            return True

        if not result_file.exists():
            pytest.skip(f'Result YAML file not found `{result_file}`')

        if not self._expected_file.exists():
            pytest.skip(f'Expected YAML file not found `{self._expected_file}`')

        # Load data to compare
        with result_file.open('r') as result_fd, self._expected_file.open('r') as expected_fd:
            self._result = yaml.safe_load(result_fd)
            self._expected = yaml.safe_load(expected_fd)

            return bool(self._result == self._expected)


    def report_compare_mismatch(self, actual: pathlib.Path) -> list[str]:
        assert self._result is not None
        assert self._expected is not None
        return [
            ''
          , f'Comparing the test result (`{actual}`) and the expected (`{self._expected_file}`) YAML files:'
          , '---[BEGIN actual result]---'
          , repr(self._result)
          , '---[END actual result]---'
          , '---[BEGIN expected result]---'
          ,  repr(self._expected)
          , '---[END expected result]---'
          ]


@pytest.fixture()
def expected_yaml(request):
    """A pytest fixture to match YAML file content."""
    return _yaml_check_or_store_pattern(
        _make_expected_filename(request, '.yaml', use_system_suffix=False)
      , store=request.config.getoption('--pm-save-patterns')
      )


#BEGIN Pytest hooks

def pytest_assertrepr_compare(op: str, left: object, right: object) -> list[str] | None:  # NOQA: PLR0911
    """Hook into comparison failure."""
    if op == '==':
        if isinstance(left, _content_match_result) and isinstance(right, bool):
            return left.report_regex_mismatch()

        if isinstance(left, _content_check_or_store_pattern) and isinstance(right, str):
            return left.report_compare_mismatch(right)

        if isinstance(right, _content_check_or_store_pattern) and isinstance(left, str):
            return right.report_compare_mismatch(left)

        # Enhance YAML checker failures
        if isinstance(left, _yaml_check_or_store_pattern) and isinstance(right, pathlib.Path):
            return left.report_compare_mismatch(right)

        if isinstance(right, _yaml_check_or_store_pattern) and isinstance(left, pathlib.Path):
            return right.report_compare_mismatch(left)

    elif op == 'is' and isinstance(left, _content_match_result) and isinstance(right, bool):
        return left.report_regex_mismatch()

    return None


# Add CLI option
def pytest_addoption(parser) -> None:
    """Add plugin options to CLI and the configuration file."""
    group = parser.getgroup('pattern-matcher')
    group.addoption(
        '--pm-save-patterns'
      , action='store_true'
        # TODO Better description
      , help='store matching patterns instead of checking them'
      )
    group.addoption(
        '--pm-patterns-base-dir'
      , metavar='PATH'
      , help='base directory to read/write pattern files'
      )

    # Also add INI file option `pm-patterns-base-dir`
    parser.addini(
        'pm-patterns-base-dir'
      , help='base directory to read/write pattern files'
      , default=None
      )
    parser.addini(
        'pm-pattern-file-use-system-name'
      , help='expect a system name (`platform.system()`) to be a pattern filename suffix'
      , default=False
      )

#END Pytest hooks
