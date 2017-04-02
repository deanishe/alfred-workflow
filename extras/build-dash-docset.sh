#!/bin/bash

basedir=$(cd $(dirname $0)/../; pwd)
docdir="${basedir}/docs"
docset="${docdir}/Alfred-Workflow.docset"
icon="${basedir}/icon.png"


echo "======================= Building Dash docset ======================="

cd "${docdir}"

if [[ -d "$docset" ]]; then
  rm -rf "$docset"
fi

doc2dash -f -n 'Alfred-Workflow' -i "${icon}" -I "quickindex.html" _build/html

cd -
