#
# SPDX-FileCopyrightText: 2017-now, See `CONTRIBUTORS.lst`
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""`pytest` plugin to match test output against expectations stored in files."""

# Local imports
from .plugin import expected_err, expected_out, pytest_addoption

__all__ = ('expected_err', 'expected_out', 'pytest_addoption')
