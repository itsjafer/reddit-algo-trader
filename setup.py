#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from os import path

from setuptools import find_packages
from setuptools import setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='redding-trending-stocks-index',
      version='0.1',
      description='Index that tracks the trending stocks on reddit',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='Jafer Haider',
      author_email='itsjafer@gmail.com',
      maintainer='itsjafer',
      maintainer_email='itsjafer@gmail.com',
      url='https://github.com/itsjafer/reddit-stocks-trending-index',
      include_package_data=True,
      packages=find_packages(),
      zip_safe=False,
      install_requires=[
      ],
      )