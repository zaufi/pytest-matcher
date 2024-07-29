#!/bin/bash
# SPDX-FileCopyrightText: 2024-now, Alex Turbov <zaufi@pm.me>
# SPDX-License-Identifier: CC0-1.0

set -e

if [[ ! -f ChangeLog.rst ]]; then
    echo "$0: Must be run from the project root directory." >&2
    exit 1
fi

# NOTE Not far than 5 lines below this marker should
# be a top (now released) version title.
declare -r MARKER_RE='^\.\. program:: pytest-matcher$'
declare -r VERSION_RE="^[0-9]+\.[0-9]+\.[0-9]+_ -- 20[0-9][0-9]-[0-1][0-9]-[0-3][0-9]$"
declare -r PRETEND_RE="${SETUPTOOLS_SCM_PRETEND_VERSION:?${SETUPTOOLS_SCM_PRETEND_VERSION//./\\.}}"

if grep -A 5 "${MARKER_RE}" ChangeLog.rst | grep -E "${VERSION_RE}" | grep -q "${PRETEND_RE}"; then
    echo "$0: ✔ Found ${SETUPTOOLS_SCM_PRETEND_VERSION} on top"
else
    echo "$0: ❌ Error: ChangeLog must be updated to include release ${SETUPTOOLS_SCM_PRETEND_VERSION}!" >&2
    exit 1
fi
