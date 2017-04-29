#!/bin/bash

rootdir=$(cd $(dirname $0)/../; pwd)

cd "${rootdir}"

/usr/bin/python setup.py sdist upload

cd -
