#!/bin/bash

# Errors are fatal
set -e

python setup.py sdist bdist_wheel
twine upload  dist/*
