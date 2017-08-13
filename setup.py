#!/usr/bin/env python
#
# Copyright (c) 2017 Alex Turbov <i.zaufi@gmail.com>
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

__version__ = '0.9.0'

setup(
    name='pytest-matcher'
  , version=__version__
  , description = 'Match test output against patterns stored in files'
  , author = 'Alex Turbov'
  , author_email = 'i.zaufi@gmail.com'
  , url='http://zaufi.github.io/programming/2017/07/05/extend-pytest-with-fixtures'
  , download_url     = 'https://github.com/zaufi/pytest-matcher/archive/release/{}.tar.gz'.format(__version__)
  , packages  = find_packages(exclude=('test'))
  , entry_points = {
        'pytest11': [
            'output_pattern_match = matcher.plugin',
        ]
    }
  , classifiers=[
        'Framework :: Pytest'
      , 'Intended Audience :: Developers'
      , 'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)'
      , 'Natural Language :: English'
      , 'Programming Language :: Python :: 3'
      ]
  , keywords         = ''
  , install_requires = get_requirements_from('requirements.txt')
  )
