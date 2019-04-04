#!/usr/bin/env python
#
# Copyright (c) 2017-2019 Alex Turbov <i.zaufi@gmail.com>
#

import pathlib
from setuptools import setup, find_packages

def sources_dir():
    return pathlib.Path(__file__).parent


def get_requirements_from(filename):
    with (sources_dir() / filename).open(encoding='UTF-8') as f:
        return f.readlines()

setup(
    install_requires = get_requirements_from('requirements.txt')
  )
