#!/bin/bash

basedir=$(cd $(dirname $0); pwd)
docdir=${basedir}/doc
curdir=$(pwd)

cd "${docdir}"
make html
cd "${curdir}"
