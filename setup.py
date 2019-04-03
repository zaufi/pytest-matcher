#!/usr/bin/env python
#
# Copyright (c) 2017-2018 Alex Turbov <i.zaufi@gmail.com>
#

import pathlib
from setuptools import setup, find_packages

def sources_dir():
    return pathlib.Path(__file__).parent


def readfile(filename):
    with (sources_dir() / filename).open(encoding='UTF-8') as f:
        return f.read()


def get_requirements_from(filename):
    with (sources_dir() / filename).open(encoding='UTF-8') as f:
        return f.readlines()

__version__ = '1.2.2'

setup(
    name = 'pytest-matcher'
  , version = __version__
  , python_requires = '~=3.4'
  , description = 'Match test output against patterns stored in files'
  , long_description = readfile('README.rst')
  , long_description_content_type = 'text/x-rst'
  , author = 'Alex Turbov'
  , author_email = 'i.zaufi@gmail.com'
  , url = 'http://zaufi.github.io/programming/2017/07/05/extend-pytest-with-fixtures'
  , download_url = 'https://github.com/zaufi/pytest-matcher/archive/release/{}.tar.gz'.format(__version__)
  , project_urls = {
        'Source': 'https://github.com/zaufi/pytest-matcher'
      , 'Tracker': 'https://github.com/zaufi/pytest-matcher/issues',
      }
  , packages = find_packages(exclude=('test'))
  , entry_points = {
        'pytest11': [
            'output_pattern_match = matcher.plugin',
        ]
    }
  , classifiers = [
        'Framework :: Pytest'
      , 'Intended Audience :: Developers'
      , 'Development Status :: 5 - Production/Stable'
      , 'Topic :: Software Development :: Testing'
      , 'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)'
      , 'Natural Language :: English'
      , 'Programming Language :: Python :: 3.4'
      , 'Programming Language :: Python :: 3.5'
      , 'Programming Language :: Python :: 3.6'
      ]
  , keywords = 'pytest plugin'
  , install_requires = get_requirements_from('requirements.txt')
  )
