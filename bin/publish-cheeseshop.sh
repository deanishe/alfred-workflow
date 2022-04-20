#!/usr/bin/env zsh

set -e

rootdir=$(cd $(dirname $0)/../; pwd)

cd "${rootdir}"
version=$( cat workflow/version )

/usr/bin/python3 setup.py sdist
twine upload dist/Alfred-Workflow-$version.tar.gz

cd -
