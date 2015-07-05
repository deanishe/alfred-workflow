#!/bin/bash

basedir=$(cd $(dirname $0)/../; pwd)
docdir="${basedir}/docs"
icon="${basedir}/icon.png"


echo "######################################################################"
echo "Building Dash docset"
echo "######################################################################"

cd "${docdir}"
doc2dash -f -n 'Alfred-Workflow' -i "${icon}" _build/html
cd -
