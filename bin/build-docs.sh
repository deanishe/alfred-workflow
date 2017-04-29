#!/bin/bash

basedir=$(cd $(dirname $0)/../; pwd)
docdir="${basedir}/docs"


echo "========================= Building docs =============================="

cd "${docdir}"
if [[ -d _build ]]; then
	rm -rf _build/*
fi
make html
cd -
