#
# SPDX-FileCopyrightText: 2017-now, See `CONTRIBUTORS.lst`
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Demonstration tests."""

# Standard imports
from datetime import datetime

# Third party packages
import pytest


def test_foo(capfd, expected_out) -> None:
    """Plain text demonstration test."""
    print('foo')

    stdout, _ = capfd.readouterr()

    assert stdout == expected_out


def test_regex(capfd, expected_out) -> None:
    """Regular-expression demonstration test."""
    print(f'Current date: {datetime.now()}')
    print(f'Current module: {__file__}')

    stdout, _ = capfd.readouterr()

    assert expected_out.match(stdout) == True


@pytest.mark.on_store(
    replace_matched_lines=[
        # Replace lines that match this regular expression with itself.
        r'Current date: [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?'
      , r'Current module: .*/tests/test_foo.py'
      ]
  )
def test_on_store_marker(capfd, expected_out) -> None:
    """Edit stored pattern demonstration test."""
    print('The beginning of a static text that never changes from run to run.')
    print(f'Current date: {datetime.now()}')
    print(f'Current module: {__file__}')
    print('The text *may have* regex special(?) metacharacters that [would be] escaped properly.')
    stdout, _ = capfd.readouterr()
    assert expected_out.match(stdout) == True


@pytest.mark.xfail(reason='Demo for diff show')
def test_diff(capfd, expected_out) -> None:
    """Plain text demonstration test that shows diff output."""
    print('Hello Africa!\nHow are you doing?', end='')

    stdout, _ = capfd.readouterr()

    assert stdout == expected_out
