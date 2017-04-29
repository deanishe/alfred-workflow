#!/bin/bash

set -e

basedir=$(cd $(dirname $0)/../; pwd)
docdir="${basedir}/docs"
docset="Alfred-Workflow.docset"
zipfile="${docset}.zip"
icon="${basedir}/icon.png"


echo "======================= Building Dash docset ======================="

cd "${docdir}"

if [[ -d "$docset" ]]; then
  command rm -rf "$docset"
fi

if [[ -f "$zipfile" ]]; then
  command rm -f "$zipfile"
fi

doc2dash -f -n 'Alfred-Workflow' -i "${icon}" -I "quickindex.html" _build/html
zip -rq "$zipfile" "$docset"
command rm -rf "$docset"

cd - &>/dev/null

echo "Saved Dash docset to $zipfile"
