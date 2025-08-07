#
# SPDX-FileCopyrightText: 2017-now, See `CONTRIBUTORS.lst`
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Test fixtures."""

# Standard imports
import pathlib
from dataclasses import dataclass

# Third party packages
import pytest

pytest_plugins = ['pytester']


@dataclass
class _ExpectDir:
    path: pathlib.Path

    def makepatternfile(self, ext: str, **kwargs: str) -> pathlib.Path:
        ret = None
        for name, content in kwargs.items():
            # NOTE Getting an indentation (to remove) by the
            # first line in the given snippet!
            if content[0].isspace():
                indent = len(content) - len(content.lstrip()) - 1
                content = '\n'.join(                        # NOQA: PLW2901
                    line[indent:]
                    for line in content.splitlines()
                  ).strip()
            p = (self.path / name).with_suffix(ext)
            p.write_text(content)
            if ret is None:
                ret = p
        assert ret is not None
        return ret


@pytest.fixture
def ourtestdir(request: pytest.FixtureRequest, pytester: pytest.Pytester) -> pytest.Pytester:
    """Pytest fixture that writes a sample ``pytest.ini`` with ``pm-patterns-base-dir`` preset."""
    default_options = {
        'addopts': '-vv -ra'
      , 'pm-patterns-base-dir': '.'
      }

    if pytest_ini_options_marker := request.node.get_closest_marker('pytest_ini_options'):
        default_options.update({
            key.replace('_', '-'): value
            for key, value in pytest_ini_options_marker.kwargs.items()
          })

    pytester.makefile(
        '.ini'
      , pytest='\n'.join([
            '[pytest]'
          , *(f'{key} = {value}' for key, value in default_options.items())
          ])
      )
    return pytester


@pytest.fixture
def expectdir(pytester: pytest.Pytester, request: pytest.FixtureRequest) -> _ExpectDir:
    """Pytest fixture that writes sample pattern files."""
    path = pytester.path / request.function.__name__
    path.mkdir()
    return _ExpectDir(path)


# BEGIN Pytest hooks
@pytest.hookimpl(trylast=True)
def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers for our tests."""
    config.addinivalue_line(
        'markers'
      , 'pytest_ini_options(args...): write a pytest.ini with the given keys and values'
      )
# END Pytest hooks
