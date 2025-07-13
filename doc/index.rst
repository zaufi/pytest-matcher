.. SPDX-FileCopyrightText: 2017-now, See ``CONTRIBUTORS.lst``
.. SPDX-License-Identifier: CC0-1.0

:Date: |today|

Welcome to Pytest Matcher documentation!
========================================

This is a ``pytest`` plugin that provides a couple of fixtures to match test output against
patterns stored in files. Expectation files are kept in a base directory, and additional
paths are derived from the test module name, test class name and test function name. Keeping
expectation files separate from tests reduces test code and allows matching more than just a
few lines of output.

.. toctree::
    :maxdepth: 1
    :caption: Contents:

    getting-started
    cli
    configuration
    api
    latest-changelog


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
