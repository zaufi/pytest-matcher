#
# SPDX-FileCopyrightText: 2017-now, See `CONTRIBUTORS.lst`
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Demo tests."""

# Standard imports
from datetime import datetime

# Third party packages
import pytest


def test_foo(capfd, expected_out) -> None:
    """Plain text demo test."""
    print('foo')

    stdout, _ = capfd.readouterr()

    assert stdout == expected_out


def test_regex(capfd, expected_out) -> None:
    """Regex demo test."""
    print(f'Current date: {datetime.now()}')
    print(f'Current module: {__file__}')

    stdout, _ = capfd.readouterr()

    assert expected_out.match(stdout) ==True


@pytest.mark.xfail(reason='Demo for diff show')
def test_diff(capfd, expected_out) -> None:
    """Plain text demo test with diff."""
    print('Hello Africa!\nHow are you doing?', end='')

    stdout, _ = capfd.readouterr()

    assert stdout == expected_out
