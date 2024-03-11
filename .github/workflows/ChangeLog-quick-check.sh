#!/bin/bash
# SPDX-FileCopyrightText: 2024-now, Alex Turbov <zaufi@pm.me>
# SPDX-License-Identifier: CC0-1.0

set -e

# NOTE Not far than 5 lines below this marker should
# be a top (now released) version title.
declare -r MARKER='.. program:: pytest-matcher'
declare -r VERSION_RE="^${SETUPTOOLS_SCM_PRETEND_VERSION:?}_ -- 20[0-9][0-9]-[0-9][0-9]-[0-9][0-9]$"

if grep -A 5 "${MARKER}" ChangeLog.rst | grep -q "${VERSION_RE}"; then
    echo "$0: ✔ Found ${SETUPTOOLS_SCM_PRETEND_VERSION} on top"
else
    echo "$0: ❌ Error: ChageLog must be updated to include release ${SETUPTOOLS_SCM_PRETEND_VERSION}!" >&2
    exit 1
fi
