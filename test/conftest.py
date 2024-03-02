#
# SPDX-FileCopyrightText: 2017-now, See `CONTRIBUTORS.lst`
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Fixtures."""

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


@pytest.fixture()
def ourtestdir(pytester: pytest.Pytester) -> pytest.Pytester:
    """Pytest fixture to write a sample `pytest.ini` w/ `pm-patterns-base-dir` preset."""
    pytester.makefile(
        '.ini'
      , pytest="""
            [pytest]
            addopts = -vv -ra
            pm-patterns-base-dir = .
        """
      )
    return pytester


@pytest.fixture()
def expectdir(pytester: pytest.Pytester, request: pytest.FixtureRequest) -> _ExpectDir:
    """Pytest fixture to write sample pattern files."""
    path = pytester.path / request.function.__name__
    path.mkdir()
    return _ExpectDir(path)
