==========
Change Log
==========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog`_ and this project adheres
to `Semantic Versioning`_.

.. _Keep a Changelog: http://keepachangelog.com/
.. _Semantic Versioning: http://semver.org/


Unreleased_
===========

Added
-----

- Use ``pytest.skip()`` if no pattern file has found or it contains an invalid regular expression.

Changed
-------

- Ensure full pattern match for ``expected_xxx.match()`` named fixtures.


1.0.0_ -- 2017-08-25
====================

Added
-----

- Add pretty printer for failed asserts with ``expected_out`` fixture and equal comparition operator.


.. _Unreleased: https://github.com/onixsol/ecm/compare/release/1.0.0...HEAD
.. _1.0.0: https://github.com/onixsol/ecm/compare/release/0.9.0...1.0.0
