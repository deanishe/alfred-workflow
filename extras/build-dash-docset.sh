#!/bin/bash

basedir=$(cd $(dirname $0)/../; pwd)
docdir="${basedir}/docs"
icon="${basedir}/icon.png"


echo "=================== Building Dash docset ============================="

cd "${docdir}"

doc2dash -f -n 'Alfred-Workflow' -i "${icon}" -I "quickindex.html" _build/html

cd -
