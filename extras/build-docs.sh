#!/bin/bash

basedir=$(cd $(dirname $0)/../; pwd)
docdir="${basedir}/docs"


echo "######################################################################"
echo "Building docs"
echo "######################################################################"

cd "${docdir}"
if [[ -d _build/html ]]; then
	rm -rf _build/html
fi
make html
cd -
