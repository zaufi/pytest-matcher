# -*- coding: utf-8 -*-
#
# Copyright (c) 2017-2018 Alex Turbov <i.zaufi@gmail.com>
#
# Pytest-match plugin is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pytest-match plugin is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

# Standard imports
import pathlib
import platform
import pytest
import re
import shutil
import sys
import yaml

class _content_check_or_store_pattern:

    def __init__(self, filename, store):
        self._pattern_filename = filename
        self._store = store
        self._expected_file_content = None


    def _store_pattern_handle_error(fn):
        def _inner(self, text):
            # Check if `--save-patterns` has given to CLI
            if self._store:
                # Make a directory to store a pattern file if it doesn't exist yet
                if not self._pattern_filename.parent.exists():
                    self._pattern_filename.parent.mkdir(parents=True)

                # Store!
                # NOTE Python >= 3.5 needed
                self._pattern_filename.write_text(text)

                return True

            # Ok, this is the "normal" check:
            # - make sure the pattern file exists
            if not self._pattern_filename.exists():
                pytest.skip('Pattern file not found `{}`'.format(self._pattern_filename))
                return False

            # - call wrapped function to
            return fn(self, text)

        return _inner


    def _read_expected_file_content(self):
        # TODO Use Python 3.5 only
        if sys.version_info >= (3, 5):
            self._expected_file_content = self._pattern_filename.read_text()
        else:
            # TODO Remove this
            with self._pattern_filename.open('r') as fd:
                self._expected_file_content = fd.read()

        assert self._expected_file_content is not None


    @_store_pattern_handle_error
    def __eq__(self, text):
        self._read_expected_file_content()
        return self._expected_file_content == text


    @_store_pattern_handle_error
    def match(self, text, flags=0):
        self._read_expected_file_content()
        content = ' '.join(self._expected_file_content.strip().splitlines())
        try:
            what = re.compile(content, flags=flags)

        except Exception as ex:
            pytest.skip('Compile a regualr expression from pattern failed: {}'.format(str(ex)))
            return False

        transformed_text = ' '.join(text.splitlines())
        m = what.fullmatch(transformed_text)
        return m is not None and bool(m)


    def report_compare_mismatch(self, actual):
        assert self._expected_file_content is not None
        return [
            'Comparing test output and expected (from `{}`):'.format(self._pattern_filename)
          , '---[BEGIN actual output]---'
          ] + actual.splitlines() + [
            '---[END actual output]---'
          , '---[BEGIN expected output]---'
          ] + self._expected_file_content.splitlines() + [
            '---[END expected output]---'
          ]


def _try_cli_option(request):
    result = request.config.getoption('--pm-patterns-base-dir')
    return (pathlib.Path(result) if result is not None else None, True)


def _try_ini_option(request):
    result = request.config.getini('pm-patterns-base-dir')
    return (pathlib.Path(result) if result else None, False)


def _try_module_path(request):
    assert request.fspath.dirname is not None
    # NOTE Suppose the current test module's directory has `data/expected/` inside
    return (pathlib.Path(request.fspath.dirname) / 'data' / 'expected', False)


def _make_expected_filename(request, ext: str, use_system_suffix=True) -> pathlib.Path:
    result = None
    use_cwd_as_base = False
    for alg in [_try_cli_option, _try_ini_option, _try_module_path]:
        result, use_cwd_as_base = alg(request)
        if result is not None:
            break

    assert result is not None

    if use_system_suffix:
        use_system_suffix = request.config.getini('pm-pattern-file-use-system-name')
        use_system_suffix = True if use_system_suffix == 'true' or use_system_suffix == '1' else False

    # Make the found path absolute using pytest's rootdir as the base
    if not result.is_absolute():
        if use_cwd_as_base:
            result = pathlib.Path.cwd()
        elif request.config.inifile is not None:
            result = pathlib.Path(request.config.inifile.dirname) / result
        else:
            assert 0

    # Make sure base directory exists
    if not result.exists():
        raise pytest.skip('Base directory for pattern-matcher do not exists: `{}`'.format(result))

    if request.cls is not None:
        result /= request.cls.__name__

    result /= request.function.__name__ \
      + ('-' + platform.system() if use_system_suffix else '') \
      + ext

    return result


@pytest.fixture
def expected_out(request):
    '''
        A pytest fixture to match `STDOUT` against a file.
    '''
    return _content_check_or_store_pattern(
        _make_expected_filename(request, '.out')
      , request.config.getoption('--pm-save-patterns')
      )


@pytest.fixture
def expected_err(request):
    '''
        A pytest fixture to match `STDERR` against a file.
    '''
    return _content_check_or_store_pattern(
        _make_expected_filename(request, '.err')
      , request.config.getoption('--pm-save-patterns')
      )


class _yaml_check_or_store_pattern:

    def __init__(self, filename, store):
        self._expected_file = filename
        self._store = store


    def _store_pattern_file(self, result_file):
        assert self._store, 'Code review required!'

        if not self._expected_file.parent.exists():
            self._expected_file.parent.mkdir(parents=True)

        shutil.copy(str(result_file), str(self._expected_file))



    def __eq__(self, result_file):
        assert isinstance(result_file, pathlib.Path)

        if self._store:
            self._store_pattern_file(result_file)
            return True

        if not result_file.exists():
            pytest.skip('Result YAML file not found `{}`'.format(result_file))
            return False

        if not self._expected_file.exists():
            pytest.skip('Expected YAML file not found `{}`'.format(self._expected_file))
            return False

        # Load data to compare
        with result_file.open('r') as result_fd, self._expected_file.open('r') as expected_fd:
            self._result = yaml.safe_load(result_fd)
            self._expected = yaml.safe_load(expected_fd)

        return self._result == self._expected


    def report_compare_mismatch(self, actual):
        assert self._result is not None
        assert self._expected is not None
        return [
            'Comparing test result (`{}`) and expected (`{}`) YAMLs:'.format(
                    actual
                  , self._expected_file
                  )
          , '---[BEGIN actual result]---'
          ] + [ repr(self._result) ] + [
            '---[END actual result]---'
          , '---[BEGIN expected result]---'
          ] + [ repr(self._expected) ] + [
            '---[END expected result]---'
          ]


@pytest.fixture
def expected_yaml(request):
    return _yaml_check_or_store_pattern(
        _make_expected_filename(request, '.yaml', use_system_suffix=False)
      , request.config.getoption('--pm-save-patterns')
      )


#BEGIN Pytest hooks

# Hook into comparision failure
def pytest_assertrepr_compare(op, left, right):
    if isinstance(left, _content_check_or_store_pattern) and isinstance(right, str) and op == "==":
        return left.report_compare_mismatch(right)

    if isinstance(right, _content_check_or_store_pattern) and isinstance(left, str) and op == "==":
        return right.report_compare_mismatch(left)

    # Enhace YAML checker failures
    if isinstance(left, _yaml_check_or_store_pattern) and isinstance(right, pathlib.Path) and op == "==":
        return left.report_compare_mismatch(right)

    if isinstance(right, _yaml_check_or_store_pattern) and isinstance(left, pathlib.Path) and op == "==":
        return right.report_compare_mismatch(left)


# Add CLI option
def pytest_addoption(parser):
    # Add a couple of CLI options into a dedicated group
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
