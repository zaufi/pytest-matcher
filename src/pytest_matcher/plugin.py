#
# SPDX-FileCopyrightText: 2017-now, See `CONTRIBUTORS.lst`
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""A ``pytest`` plugin that matches test output against expectation files."""

from __future__ import annotations

# Standard imports
import difflib
import enum
import functools
import os
import pathlib
import platform
import re
import shutil
import string
import sys
import urllib.parse
from dataclasses import InitVar, astuple, dataclass, field
from typing import TYPE_CHECKING, Any, Final, TextIO, cast

if TYPE_CHECKING:
    from collections.abc import Iterable

# Third party packages
import pytest
import yaml

try:
    from pygments import highlight
    from pygments.formatters import TerminalFormatter
    from pygments.lexers import DiffLexer

    HAVE_PYGMENTS = True
    # ATTENTION THIS IS THE UGLY IMPORT OF PYTEST IMPLEMENTATION DETAILS
    # BUT UNFORTUNATELY I SEE NO OTHER WAY (and I don't like copy-n-paste %-)
    from _pytest._io.terminalwriter import should_do_markup

except ImportError:
    HAVE_PYGMENTS = False

    def should_do_markup(_: TextIO) -> bool:                # type: ignore[misc]
        """Fallback stub used when the optional dependency cannot be imported."""
        return False


PM_COLOR_OUTPUT = pytest.StashKey[bool]()

ON_STORE_KWARGS_INT: Final[set[str]] = {
    'drop_head'
  , 'drop_tail'
  }
ON_STORE_KWARGS_STR: Final[set[str]] = {
    'replace_matched_lines'
  }
ON_STORE_KWARGS: Final[set[str]] = ON_STORE_KWARGS_INT | ON_STORE_KWARGS_STR


_EOL_RE: Final[re.Pattern] = re.compile('(\r?\n|\r)')

if sys.version_info < (3, 11):
    _RE_NOFLAG: Final[re.RegexFlag] = cast('re.RegexFlag', 0)
else:
    _RE_NOFLAG: Final[re.RegexFlag] = re.NOFLAG


class _MismatchStyle(enum.Enum):
    FULL = enum.auto()
    DIFF = enum.auto()


@dataclass
class _ContentMatchResult:                                  # NOQA: PLW1641
    """Result of matching text content against a regular expression."""

    result: bool
    text: list[str]
    regex: str
    filename: pathlib.Path

    def __eq__(self, other: object) -> bool:
        return isinstance(other, bool) and self.result == other

    def __bool__(self) -> bool:
        return self.result

    def report_regex_mismatch(self) -> list[str]:
        return [
            ''
          , "The test output doesn't match the expected regex."
          , f'(from `{self.filename}`):'
          , '---[BEGIN actual output]---'
          , *self.text
          , '---[END actual output]---'
          , '---[BEGIN expected regex]---'
          , *self.regex.splitlines()
          , '---[END expected regex]---'
          ]


@dataclass
class _ContentEditParameters:
    replace_matched_lines_raw: InitVar[list[str] | None] = None
    replace_matched_lines: list[re.Pattern] = field(default_factory=list, init=False)
    drop_head: int = 0
    drop_tail: int = 0

    def __post_init__(self, replace_matched_lines_raw: list[str] | None) -> None:
        self.replace_matched_lines = functools.reduce(
            self._str2re
          , replace_matched_lines_raw if replace_matched_lines_raw is not None else []
          , []
          )
        self._check_and_report_drop_value(self.drop_head, 'drop_head')
        self._check_and_report_drop_value(self.drop_tail, 'drop_tail')

    def _str2re(self, state: list[re.Pattern], raw_re: str) -> list[re.Pattern]:
        try:
            return [*state, re.compile(raw_re)]
        except re.error as ex:
            msg = f"'on_store' marker got invalid regular expression: '{raw_re}'"
            raise pytest.UsageError(msg) from ex

    def _check_and_report_drop_value(self, value: int, param_name: str) -> None:
        if value < 0:
            msg = f"'on_store' marker got invalid value `{value!s}` for parameter '{param_name}'"
            raise pytest.UsageError(msg)

    def _edit_line(self, state: Iterable[str], line: str) -> Iterable[str]:
        if self.replace_matched_lines:
            re_line = functools.reduce(
                lambda text, regex: re.sub(regex, regex.pattern, text)
              , self.replace_matched_lines
              , line
              )
            # Escape regex symbols if line doesn't match
            line = self._regex_escape(line) if re_line == line else re_line

        else:
            line = self._regex_escape(line)

        return [*state, line]

    def edit_text(self, text: str) -> str:
        lines = text.splitlines()
        # Write `.*` pattern as the very first line to match any content that has been dropped...
        return ('.*\n' if self.drop_head else '') + '\n'.join(
            functools.reduce(
                self._edit_line
              , lines[self.drop_head : len(lines) - self.drop_tail]
              , []
              )
          ) + '\n'

    def is_edit_requested(self) -> bool:
        return bool(self.drop_head) or bool(self.drop_tail) or bool(self.replace_matched_lines)

    @staticmethod
    def _regex_escape(text: str) -> str:
        return re.escape(text).replace('\\ ', ' ')


@dataclass
class _ContentCheckOrStorePattern:                          # NOQA: PLW1641

    pattern_filename: pathlib.Path
    store: bool
    edit: _ContentEditParameters

    @functools.cached_property
    def expected_file_content(self) -> str:
        if not (self.pattern_filename.exists() and self.pattern_filename.is_file()):
            pytest.skip(f'Pattern file not found `{self.pattern_filename}`')

        return self.pattern_filename.read_text()

    def __eq__(self, text: object) -> bool:
        if not isinstance(text, str):
            msg = 'An argument to `__eq__` must be `str` type'
            raise TypeError(msg)

        self._maybe_store_pattern(text)
        return self.expected_file_content == text

    def __str__(self) -> str:
        return self.expected_file_content

    def __repr__(self) -> str:
        return f"(pattern_filename='{self.pattern_filename!s}', pattern='{self.expected_file_content}')"

    def match(self, text: str, flags: re.RegexFlag = _RE_NOFLAG) -> _ContentMatchResult:
        self._maybe_store_pattern(text)
        content = (
            '.*\n' if flags & re.MULTILINE else ' '
          ).join(
              self.expected_file_content.strip().splitlines()
            )
        try:
            if flags & re.MULTILINE:
                what = re.compile('.*' + content + '.*', flags=flags)
            else:
                what = re.compile(content, flags=flags)

        except re.error as ex:
            pytest.skip(
                f'Compiling the regular expression from the pattern failed: {ex!s}'
              )

        text_lines = text.splitlines()

        m = what.fullmatch(('\n' if flags & re.MULTILINE else ' ').join(text_lines))
        return _ContentMatchResult(
            result=m is not None and bool(m)
          , text=text_lines
          , regex=self.expected_file_content
          , filename=self.pattern_filename
          )

    def report_compare_mismatch(self, actual: str, *, color: bool, style: _MismatchStyle) -> list[str]:
        return (
            self._report_mismatch_diff(actual, color=color)
            if style == _MismatchStyle.DIFF
            else self._report_mismatch_text(actual, color=color)
          )

    # BEGIN Private members
    def _maybe_store_pattern(self, text: str) -> None:
        if not self.store:
            return

        # Make a directory to store a pattern file if it doesn't exist yet
        if not self.pattern_filename.parent.exists():
            self.pattern_filename.parent.mkdir(parents=True)

        # Store!
        self.pattern_filename.write_text(
            self.edit.edit_text(text)
            if self.edit.is_edit_requested()
            else text
          )

        # Also mark the test as skipped!
        pytest.skip(f'Pattern file saved to `{self.pattern_filename}`.')

    def _make_newlines_visible(self, text: str) -> str:
        return _EOL_RE.sub(r'↵\1', text)

    def _report_mismatch_text(self, actual: str, *, color: bool) -> list[str]:  # NOQA: ARG002
        return [
            ''
          , "The test output doesn't match the expected output."
          , f'(from `{self.pattern_filename}`):'
          , '---[BEGIN actual output]---'
          , *self._make_newlines_visible(actual).splitlines()
          , '---[END actual output]---'
          , '---[BEGIN expected output]---'
          , *self._make_newlines_visible(self.expected_file_content).splitlines()
          , '---[END expected output]---'
          ]

    def _report_mismatch_diff(self, actual: str, *, color: bool) -> list[str]:
        diff=[
            *difflib.unified_diff(
                self._make_newlines_visible(self.expected_file_content).splitlines()
              , self._make_newlines_visible(actual).splitlines()
              , fromfile='expected'
              , tofile='actual'
              , lineterm=''
              )
          ]

        if HAVE_PYGMENTS and color:
            colored_diff = highlight(
                '\n'.join(diff)
              , DiffLexer()
              , TerminalFormatter(
                    # NOTE Here we don't care about incorrect values
                    # of envvars cuz `pytest` already made an instance
                    # of `TerminalWriter` which handles this situation!
                    bg=os.getenv('PYTEST_THEME_MODE', 'dark')
                  , style=os.getenv('PYTEST_THEME')
                  )
              )
            diff = colored_diff.splitlines()

        return [
            ''
          , "The test output doesn't match the expected output."
          , f'(from `{self.pattern_filename}`):'
          , '---[BEGIN expected vs actual diff]---'
          , *diff
          , '---[END expected vs actual diff]---'
          ]
    # END Private members


def _get_base_dir(config: pytest.Config) -> pathlib.Path:
    result: pathlib.Path | None = config.getoption('--pm-patterns-base-dir')
    return (
        result
        if result is not None
        else pathlib.Path(config.getini('pm-patterns-base-dir'))
      )


def _subst_pattern_parts(result: pathlib.Path, current: str, **kwargs: str) -> pathlib.Path:
    # ATTENTION If pattern format started w/ `/`
    # (or containing it in any place), just ignore it!
    if current == '/':
        return result
    part = current.format(**kwargs)
    return result / part if part else result


def _make_expected_filename(request: pytest.FixtureRequest, ext: str) -> pathlib.Path:
    result = request.config.rootpath / _get_base_dir(request.config)

    # Make sure base directory exists
    if not result.exists():
        pytest.skip(f'Base directory for pattern-matcher does not exist: `{result}`')

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

    subst = {
        'module': request.module.__name__.split('.')[-1]
      , 'class': request.cls.__name__ if request.cls is not None else ''
      , 'fn': request.function.__name__
      , 'callspec': urllib.parse.quote(
            request.node.name[len(request.function.__name__):]
          , safe='[]'
          )
      , 'suffix': ('','-')[int(bool(args))] + urllib.parse.quote('-'.join(args), safe='[]')
      }

    result = functools.reduce(
        functools.partial(_subst_pattern_parts, **subst)
      , pathlib.Path(request.config.getini('pm-pattern-file-fmt')).parts
      , result
      )
    return result.with_suffix(result.suffix + ext)


@dataclass
class _OnStoreParamsReducerState:
    ctor_args: dict[str, list[str] | int] = field(default_factory=dict)
    unsupported: list[str] = field(default_factory=list)
    invalid_type: list[str] = field(default_factory=list)


def _collect_on_store_param(
    state: _OnStoreParamsReducerState
  , item: tuple[str, Any]
  ) -> _OnStoreParamsReducerState:

    def _is_list_of_strings(value: list[Any]) -> bool:
        return isinstance(value, list) and all(isinstance(item, str) for item in value)

    match item:
        case (key, int() as value) if key in ON_STORE_KWARGS_INT:
            state.ctor_args[key] = value

        case (key, value) if _is_list_of_strings(value) and key in ON_STORE_KWARGS_STR:
            state.ctor_args[f'{key}_raw'] = value

        case (key, _) if key in ON_STORE_KWARGS:
            state.invalid_type.append(key)

        case (key, _):
            state.unsupported.append(key)

    return state


def _try_get_on_store_params(request: pytest.FixtureRequest) -> _ContentEditParameters:
    on_store = request.node.get_closest_marker('on_store')
    if on_store is None:
        return _ContentEditParameters()

    ctor_args, unsupported, invalid_type = astuple(
        functools.reduce(
            _collect_on_store_param
          , on_store.kwargs.items()
          , _OnStoreParamsReducerState()
          )
      )

    def _report_problem(items: list[str], fmt: str) -> None:
        if items:
            msg = fmt.format(
                plural='s' if len(items) > 1 else ''
              , items="'" + "', '".join(items) + "'"
              )
            raise pytest.UsageError(msg)

    _report_problem(
        invalid_type
      , "'on_store' marker got parameter{plural} with invalid type: {items}"
      )
    _report_problem(
        unsupported
      , "'on_store' marker got invalid parameter{plural}: {items}"
      )

    return _ContentEditParameters(**ctor_args)


@pytest.fixture
def expected_out(request: pytest.FixtureRequest) -> _ContentCheckOrStorePattern:
    """Pytest fixture for matching ``STDOUT`` against a file."""
    return _ContentCheckOrStorePattern(
        _make_expected_filename(request, '.out')
      , store=request.config.getoption('--pm-save-patterns')
      , edit=_try_get_on_store_params(request)
      )


@pytest.fixture
def expected_err(request: pytest.FixtureRequest) -> _ContentCheckOrStorePattern:
    """Pytest fixture for matching ``STDERR`` against a file."""
    return _ContentCheckOrStorePattern(
        _make_expected_filename(request, '.err')
      , store=request.config.getoption('--pm-save-patterns')
      , edit=_try_get_on_store_params(request)
      )


@dataclass
class _YAMLCheckOrStorePattern:                             # NOQA: PLW1641

    expected_file: pathlib.Path
    store: bool
    result: object | None = None
    expected: object | None = None

    def _store_pattern_file(self, result_file: pathlib.Path) -> None:
        assert self.store, 'Code review required!'

        if not self.expected_file.parent.exists():
            self.expected_file.parent.mkdir(parents=True)

        assert self.expected_file.parent.is_dir()

        shutil.copy(str(result_file), str(self.expected_file))

    def __eq__(self, result_file: object) -> bool:
        assert isinstance(result_file, pathlib.Path)

        if self.store:
            self._store_pattern_file(result_file)
            return True

        if not result_file.exists():
            pytest.skip(f'Result YAML file not found `{result_file}`')

        if not self.expected_file.exists():
            pytest.skip(f'Expected YAML file not found `{self.expected_file}`')

        # Load data to compare
        with result_file.open('r') as result_fd, self.expected_file.open('r') as expected_fd:
            self.result = yaml.safe_load(result_fd)
            self.expected = yaml.safe_load(expected_fd)

            return bool(self.result == self.expected)

    def report_compare_mismatch(self, actual: pathlib.Path) -> list[str]:
        assert self.result is not None
        assert self.expected is not None
        return [
            ''
          , f'Comparing the test result (`{actual}`) with the expected YAML file (`{self.expected_file}`):'
          , '---[BEGIN actual result]---'
          , repr(self.result)
          , '---[END actual result]---'
          , '---[BEGIN expected result]---'
          ,  repr(self.expected)
          , '---[END expected result]---'
          ]


@pytest.fixture
def expected_yaml(request: pytest.FixtureRequest) -> _YAMLCheckOrStorePattern:
    """Pytest fixture for matching YAML file content."""
    return _YAMLCheckOrStorePattern(
        _make_expected_filename(request, '.yaml')
      , store=request.config.getoption('--pm-save-patterns')
      )


class _UnusedFilesReporter:
    """Reporter that reveals unused pattern files."""
    def __init__(self, *, return_codes: bool = False) -> None:
        self._return_codes = return_codes

    def pytest_collection_finish(self, session: pytest.Session) -> None:
        """Check for and display unused files after collection."""
        if not session.items:
            return

        patterns_base_dir = session.config.rootpath / _get_base_dir(session.config)
        known_extensions = '.out', '.err'

        all_paths = {
            p.resolve()
            for p in patterns_base_dir.rglob('*')
            if p.is_file() and p.suffix in known_extensions
          }

        collected_paths = {
            _make_expected_filename(item._request, ext)     # type: ignore[attr-defined] # NOQA: SLF001
            for item in session.items
            for fixture, ext in zip((expected_out, expected_err), known_extensions, strict=True)
            if fixture.__name__ in item.fixturenames        # type: ignore[attr-defined]
          }

        unused_paths = all_paths - collected_paths
        if unused_paths:
            sys.stdout.write('\n'.join(map(str, sorted(unused_paths))) + '\n')
            if self._return_codes:
                pytest.exit('Found unused pattern files', 1)


def _get_mismatch_output_style(config: pytest.Config) -> _MismatchStyle:
    style_str = config.getoption('--pm-mismatch-style')
    if style_str is None:
        style_str = config.getini('pm-mismatch-style')
    assert style_str is not None
    return _MismatchStyle[style_str.upper()]


# BEGIN Pytest hooks

def pytest_assertrepr_compare(                              # NOQA: PLR0911
    config: pytest.Config
  , op: str
  , left: object
  , right: object
  ) -> list[str] | None:
    """Hook executed when assertion comparisons fail."""
    if op == '==':
        match left, right:
            case _ContentMatchResult() as left, bool(right):
                return left.report_regex_mismatch()

            case _ContentCheckOrStorePattern() as left, str(right):
                return left.report_compare_mismatch(
                    right
                  , style=_get_mismatch_output_style(config)
                  , color=config.stash[PM_COLOR_OUTPUT]
                  )

            case str(left), _ContentCheckOrStorePattern() as right:
                return right.report_compare_mismatch(
                    left
                  , style=_get_mismatch_output_style(config)
                  , color=config.stash[PM_COLOR_OUTPUT]
                  )

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
    """Add plugin options to the command-line interface and configuration file."""
    group = parser.getgroup('pattern matcher')
    group.addoption(
        '--pm-save-patterns'
      , action='store_true'
      , help='Save captured output to pattern files and skip the test.'
      )
    group.addoption(
        '--pm-mismatch-style'
      , type=str
      , help='Style of the mismatch report when expected and actual outputs differ.'
      , choices=[style.name.lower() for style in _MismatchStyle]
      , default=None
      )
    group.addoption(
        '--pm-patterns-base-dir'
      , metavar='PATH'
      , help='Base directory used for storing pattern files.'
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
      , help='Base directory used for storing pattern files.'
      , default=pathlib.Path('tests/data/expected')
      )
    parser.addini(
        'pm-pattern-file-fmt'
      , help='pattern filename format can use placeholders: `module`, `class`, `fn`, `callspec`, `system`'
      , type='string'
      , default='{module}/{class}/{fn}{callspec}{suffix}'
      )
    parser.addini(
        'pm-mismatch-style'
      , help='Style of the mismatch report when expected and actual outputs differ.'
      , type='string'
      , default=_MismatchStyle.FULL.name.lower()
      )


@pytest.hookimpl(trylast=True)
def pytest_configure(config: pytest.Config) -> None:
    """Validate the configuration and register the unused-files reporter."""
    config.addinivalue_line(
        'markers'
      , 'expect_suffix(args..., *, suffix="..."): mark test to have suffixed pattern file'
      )
    config.addinivalue_line(
        'markers'
      , 'on_store(**kwargs): patch an expected pattern before store'
      )

    # Make sure the patterns base directory isn't an absolute path!
    basedir = _get_base_dir(config)
    if basedir.is_absolute():
        msg = 'The patterns base directory must be relative'
        raise pytest.UsageError(msg)

    def _path_have_dot_dot(path: pathlib.Path) -> bool:
        return any(part == '..' for part in path.parts)

    # Prevent directory traversal in # `pm-pattern-file-fmt`
    # and `pm-patterns-base-dir` parameters!
    pattern_file_fmt = config.getini('pm-pattern-file-fmt')
    if any(map(_path_have_dot_dot, (basedir, pathlib.Path(pattern_file_fmt)))):
        msg = 'Directory traversal is not allowed for `pm-pattern-file-fmt` or `pm-patterns-base-dir` option'
        raise pytest.UsageError(msg)

    # Make sure the `pm-pattern-file-fmt` format string is correct
    # and there are only known placeholders!
    try:
        formatter = string.Formatter()
        placeholders = [
            placeholder
            for _, placeholder, _, _ in formatter.parse(pattern_file_fmt)
            if placeholder
          ]

        if not bool(placeholders):
            msg = "'pm-pattern-file-fmt' should have at least one placeholder"
            raise pytest.UsageError(msg)

        supported = ['module', 'class', 'fn', 'callspec', 'suffix']
        unsupported = [f"'{item}'" for item in placeholders if item not in supported]

        if unsupported:
            plural = 's' if len(unsupported) > 1 else ''
            msg = f"'pm-pattern-file-fmt' has invalid placeholder{plural}: {', '.join(unsupported)}"
            raise pytest.UsageError(msg)

    except ValueError as ex:
        msg = f"'pm-pattern-file-fmt' has incorrect format: {str(ex).lower()}"
        raise pytest.UsageError(msg) from ex

    # Validate `pm-mismatch-style` option value.
    style_str = config.getini('pm-mismatch-style')
    if style_str.upper() not in [item.name for item in _MismatchStyle]:
        msg = (
            f"'pm-mismatch-style' option have an invalid value `{style_str}`. "
            "Valid values are: `full`, `diff`."
          )
        raise pytest.UsageError(msg)

    config.stash[PM_COLOR_OUTPUT] = should_do_markup(sys.stdout)

    if not config.getoption('--pm-reveal-unused-files'):
        return

    return_codes = os.getenv('PYTEST_MATCHER_RETURN_CODES', '').lower() in ('yes', 'true', '1')
    config.option.collectonly = True
    reporter = _UnusedFilesReporter(return_codes=return_codes)
    config.pluginmanager.unregister(name='terminalreporter')
    config.pluginmanager.register(reporter, 'terminalreporter')

# END Pytest hooks
