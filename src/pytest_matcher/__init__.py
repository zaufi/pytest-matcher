#
# SPDX-FileCopyrightText: 2017-now, See `CONTRIBUTORS.lst`
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""A ``pytest`` plugin for matching test output against expectation files."""

# Local imports
from .plugin import expected_err, expected_out, pytest_addoption

__all__ = ('expected_err', 'expected_out', 'pytest_addoption')
