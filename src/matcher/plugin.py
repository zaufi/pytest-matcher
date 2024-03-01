#
# SPDX-FileCopyrightText: 2017-now, See `CONTRIBUTORS.lst`
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""A `pytest` plugin to match test output against expectations."""

from __future__ import annotations

# Standard imports
import functools
import os
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


class _ContentMatchResult:
    """TODO Is this job for Python `dataclass`?"""

    def __init__(self, *, result: bool, text: list[str], regex: str, filename: pathlib.Path) -> None:
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


class _ContentCheckOrStorePattern:

    def __init__(self, filename: pathlib.Path, *, store: bool) -> None:
        self._pattern_filename = filename
        self._store = store
        self._expected_file_content: str | None = None

    def _maybe_store_pattern(self, text: str) -> None:
        if not self._store:
            return

        # Make a directory to store a pattern file if it doesn't exist yet
        if not self._pattern_filename.parent.exists():
            self._pattern_filename.parent.mkdir(parents=True)

        # Store!
        self._pattern_filename.write_text(text)

        # Also mark the test as skipped!
        pytest.skip(f'Pattern file has been saved `{self._pattern_filename}`')

    def _read_expected_file_content(self) -> None:
        if not (self._pattern_filename.exists() and self._pattern_filename.is_file()):
            pytest.skip(f'Pattern file not found `{self._pattern_filename}`')

        self._expected_file_content = self._pattern_filename.read_text()

    def __eq__(self, text: object) -> bool:
        if not isinstance(text, str):
            msg = 'An argument to `__eq__` must be `str` type'
            raise TypeError(msg)

        self._maybe_store_pattern(text)
        self._read_expected_file_content()
        return self._expected_file_content == text

    def match(self, text: str, flags: re.RegexFlag = _RE_NOFLAG) -> _ContentMatchResult:
        self._maybe_store_pattern(text)
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
        return _ContentMatchResult(
            result=m is not None and bool(m)
          , text=text_lines
          , regex=self._expected_file_content               # type: ignore[arg-type]
          , filename=self._pattern_filename
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


def _try_cli_option(request: pytest.FixtureRequest) -> tuple[pathlib.Path | None, bool]:
    result = request.config.getoption('--pm-patterns-base-dir')
    return (pathlib.Path(result) if result is not None else None, True)


def _try_ini_option(request: pytest.FixtureRequest) -> tuple[pathlib.Path | None, bool]:
    result = request.config.getini('pm-patterns-base-dir')
    return (pathlib.Path(result) if result else None, False)


def _try_module_path(request: pytest.FixtureRequest) -> tuple[pathlib.Path, bool]:
    assert request.path.parent is not None
    # NOTE Suppose the current test module's directory has `data/expected/` inside
    return (pathlib.Path(request.path.parent) / 'data' / 'expected', False)


def _subst_pattern_parts(result: pathlib.Path, current: str, **kwargs: str) -> pathlib.Path:
    # ATTENTION If pattern format started w/ `/`
    # (or containing it in any place), just ignore it!
    if current == '/':
        return result
    part = current.format(**kwargs)
    return result / part if part else result


def _make_expected_filename(request: pytest.FixtureRequest, ext: str) -> pathlib.Path:
    result: pathlib.Path | None = None
    use_cwd_as_base = False
    for alg in [_try_cli_option, _try_ini_option, _try_module_path]:
        result, use_cwd_as_base = alg(request)
        if result is not None:
            break

    assert result is not None

    # Make the found path absolute using pytest's rootdir as the base
    if not result.is_absolute():
        if use_cwd_as_base:
            result = pathlib.Path.cwd()
        elif request.config.inipath is not None:
            result = pathlib.Path(request.config.inipath.parent) / result
        else:
            # TODO Better error description.
            pytest.fail('Unable to determine the path to expectation files')

    # Make sure base directory exists
    if not result.exists():
        pytest.skip(f'Base directory for pattern-matcher do not exists: `{result}`')

    # Check if a test function has been marked as having a
    # suffix for a pattern filename.
    args: list[str] = []
    if sfx_makrer := request.node.get_closest_marker('expect_suffix'):
        # Process positional args first
        args = [f'{arg!s}' for arg in sfx_makrer.args]
        # Also, check if `suffix` has been given as a named parameter
        if 'suffix' in sfx_makrer.kwargs:
            args.append(f'{sfx_makrer.kwargs["suffix"]!s}')

        # NOTE If marker has added w/o any arguments, assume
        # it should be a system name suffix.
        if not args:
            args.append(platform.system())

    subst: dict[str, str] = {
        'module': request.module.__name__.split('.')[-1]
      , 'class': request.cls.__name__ if request.cls is not None else ''
      , 'fn': request.function.__name__
      , 'callspec': urllib.parse.quote(
            request.node.name[len(request.function.__name__):]
          , safe='[]'
          )
      , 'suffix': ('','-')[int(bool(args))] + '-'.join(args)
      }

    return functools.reduce(
        functools.partial(_subst_pattern_parts, **subst)
      , pathlib.Path(request.config.getini('pm-pattern-file-fmt')).parts
      , result
      ).with_suffix(ext)


@pytest.fixture()
def expected_out(request: pytest.FixtureRequest) -> _ContentCheckOrStorePattern:
    """A pytest fixture to match `STDOUT` against a file."""
    return _ContentCheckOrStorePattern(
        _make_expected_filename(request, '.out')
      , store=request.config.getoption('--pm-save-patterns')
      )


@pytest.fixture()
def expected_err(request: pytest.FixtureRequest) -> _ContentCheckOrStorePattern:
    """A pytest fixture to match `STDERR` against a file."""
    return _ContentCheckOrStorePattern(
        _make_expected_filename(request, '.err')
      , store=request.config.getoption('--pm-save-patterns')
      )


class _YAMLCheckOrStorePattern:

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
def expected_yaml(request: pytest.FixtureRequest) -> _YAMLCheckOrStorePattern:
    """A pytest fixture to match YAML file content."""
    return _YAMLCheckOrStorePattern(
        _make_expected_filename(request, '.yaml')
      , store=request.config.getoption('--pm-save-patterns')
      )


class _UnusedFilesReporter:
    """A reporter to reveal unused pattern files."""
    def __init__(self, *, return_codes: bool = False) -> None:
        self._return_codes = return_codes

    def pytest_collection_finish(self, session: pytest.Session) -> None:
        """Once test items have been collected, check for and show unused files."""
        if not session.items:
            return

        for alg in [_try_cli_option, _try_ini_option]:
            patterns_base_dir, _ = alg(session.items[0]._request)  # type: ignore[attr-defined] # NOQA: SLF001
            if patterns_base_dir:
                break
        else:
            message = 'Failed to determine a patterns base directory'
            raise pytest.UsageError(message)

        known_extensions = '.out', '.err'

        all_paths = {
            p.resolve()
            for p in patterns_base_dir.rglob('*')
            if p.is_file() and p.suffix in known_extensions
          }

        collected_paths = {
            _make_expected_filename(item._request, ext)  # type: ignore[attr-defined] # NOQA: SLF001
            for item in session.items
            for fixture, ext in zip((expected_out, expected_err), known_extensions)
            if fixture.__name__ in item.fixturenames  # type: ignore[attr-defined]
          }

        unused_paths = all_paths - collected_paths
        if unused_paths:
            sys.stdout.write('\n'.join(map(str, sorted(unused_paths))) + '\n')
            if self._return_codes:
                pytest.exit('Found unused pattern files', 1)


# BEGIN Pytest hooks

def pytest_assertrepr_compare(op: str, left: object, right: object) -> list[str] | None:  # NOQA: PLR0911
    """Hook into comparison failure."""
    if op == '==':
        match left, right:
            case _ContentMatchResult() as left, bool(right):
                return left.report_regex_mismatch()

            case _ContentCheckOrStorePattern() as left, str(right):
                return left.report_compare_mismatch(right)

            case str(left), _ContentCheckOrStorePattern() as right:
                return right.report_compare_mismatch(left)

            # Enhance YAML checker failures
            case _YAMLCheckOrStorePattern() as left, pathlib.Path() as right:
                return left.report_compare_mismatch(right)

            case pathlib.Path() as left, _YAMLCheckOrStorePattern() as right:
                return right.report_compare_mismatch(left)

    elif op == 'is':
        match left, right:
            case _ContentMatchResult() as left,  bool(right):
                return left.report_regex_mismatch()

    return None


# Add CLI option
def pytest_addoption(parser: pytest.Parser) -> None:
    """Add plugin options to CLI and the configuration file."""
    group = parser.getgroup('pattern matcher')
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
      , type=pathlib.Path
      )
    group.addoption(
        '--pm-reveal-unused-files'
      , action='store_true'
      , help='reveal and print unused pattern files'
      )

    # Also add INI file (TOML table) options
    parser.addini(
        'pm-patterns-base-dir'
      , help='base directory to read/write pattern files'
      , default=None
      )
    parser.addini(
        'pm-pattern-file-fmt'
      , help='pattern filename format can use placeholders: `module`, `class`, `fn`, `callspec`, `system`'
      , type='string'
      , default='{module}/{class}/{fn}{callspec}'
      )
    parser.addini(
        'pm-pattern-file-fmt'
      , help='pattern filename format can use placeholders: `module`, `class`, `fn`, `callspec`, `system`'
      , type='string'
      , default='{module}/{class}/{fn}{callspec}{suffix}'
      )


@pytest.hookimpl(trylast=True)
def pytest_configure(config: pytest.Config) -> None:
    """Validate configuration and register additional reporter."""
    # ALERT Prevent directory traversal!
    if any(part == '..' for part in pathlib.Path(config.getini('pm-pattern-file-fmt')).parts):
        msg = 'Directory traversal is not allowed for `pm-pattern-file-fmt` option'
        raise pytest.UsageError(msg)

    if not config.getoption('--pm-reveal-unused-files'):
        return

    return_codes = os.getenv('PYTEST_MATCHER_RETURN_CODES', '').lower() in ('yes', 'true', '1')
    config.option.collectonly = True
    reporter = _UnusedFilesReporter(return_codes=return_codes)
    config.pluginmanager.unregister(name='terminalreporter')
    config.pluginmanager.register(reporter, 'terminalreporter')

# END Pytest hooks
