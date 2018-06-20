#!/usr/bin/env python

# Always prefer setuptools over distutils
import os

from setuptools import setup, find_packages

# To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))

long_description = ''

setup(
    name='graphalama',
    version='0.0',
    description='Easy to use widgets for pygame',
    long_description=long_description,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    keywords='pygame widget widgets gui llama',
    url="",
    author='Diego Dorn',
    author_email='diego.dorn@free.fr',
    packages=find_packages(),
    package_data={
        '.': ['README.*'],
    },
    include_package_data=True,
    install_requires=['pygame'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
