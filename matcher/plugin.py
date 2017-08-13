# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Alex Turbov <i.zaufi@gmail.com>
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
import pytest
import warnings


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


class _content_check_or_store_pattern:

    def __init__(self, filename, store):
        self._filename = filename
        self._store = store


    def _store_pattern_handle_error(fn):
        def _inner(self, text):
            # Check if `--save-patterns` has given to CLI
            if self._store:
                # Make directory to store pattern file if it doesn't exist yet
                if not self._filename.parent.exists():
                    self._filename.parent.mkdir(parents=True)

                # Store!
                self._filename.write_text(text)
                return True

            # Ok, this is the "normal" check:
            # - make sure the pattern file exists
            if not self._filename.exists():
                warnings.warn('Pattern file not found `{}`'.format(self._filename), RuntimeWarning)
                return False

            # - call wrapped function to
            return fn(self, text)

        return _inner


    @_store_pattern_handle_error
    def __eq__(self, text):
        expected_text = self._filename.read_text().strip()
        return expected_text == text


    @_store_pattern_handle_error
    def match(self, text):
        content = ' '.join(self._filename.read_text().strip().splitlines())
        what = re.compile(content)
        transformed_text = ' '.join(text.splitlines())
        return bool(what.match(transformed_text))


def _try_cli_option(request):
    result = request.config.getoption('--pm-patterns-base-dir')
    return pathlib.Path(result) if result is not None else None


def _try_ini_option(request):
    result = request.config.getini('pm-patterns-base-dir')
    return pathlib.Path(result) if result is not None else None


def _try_module_path(request):
    assert request.fspath.dirname is not None
    return pathlib.Path(request.fspath.dirname) / 'data' / 'expected'


def _make_expected_filename(request, ext: str) -> pathlib.Path:
    result = None
    for alg in [_try_cli_option, _try_ini_option, _try_module_path]:
        result = alg(request)
        if result is not None:
            break

    assert result is not None

    # Make sure base directory exists
    if not result.exists():
        raise ValueError('Base directory for pattern-matcher do not exists: `{}`'.format(result))

    if request.cls is not None:
        result /= request.cls.__name__

    result /= request.function.__name__ + ext

    return result


@pytest.fixture
def expected_out(request):
    return _content_check_or_store_pattern(
        _make_expected_filename(request, '.out')
      , request.config.getoption('--pm-save-patterns')
      )


@pytest.fixture
def expected_err(request):
    return _content_check_or_store_pattern(
        _make_expected_filename(request, '.err')
      , request.config.getoption('--pm-save-patterns')
      )
