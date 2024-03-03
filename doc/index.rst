.. SPDX-FileCopyrightText: 2017-now, See ``CONTRIBUTORS.lst``
.. SPDX-License-Identifier: CC0-1.0

:Date: |today|

Welcome to Pytest Matcher documentation!
========================================

This is a ``pytest`` plugin provides a couple of fixtures to match test output against patterns
stored in files.  Expectations/pattern files are stored in a base directory, and additional
paths are based on the test module name, test class name, and test function name.  Having output
expectations/pattern files separate from tests helps to reduce the code of the latter and match
the output more than just a few lines.

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
