#!/usr/bin/env python

import os
from setuptools import setup


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname), 'r') as f:
        return f.read()


setup(name='py5',
      version='1.0',
      description='Wrapper around the F5 iControl REST API.',
      long_description=read('README.md'),
      author='Corwin Brown',
      author_email='corwin.brown@maxpoint.com',
      packages=['py5', 'tests'],
      scripts=['bin/py5-cli'],
      install_requires=['requests==2.4.3', 'pyyaml==3.11'],
      test_suite='tests.test_py5.py5Tests',
      platform='all')
