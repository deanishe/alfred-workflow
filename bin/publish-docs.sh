#!/bin/bash

set -e

# Publish documentation to gh-pages branch using ghp-import

if [[ -z "$1" ]]; then
    echo "You must specify a commit message."
    exit 1
fi

# Test that ghp-import is installed
command -v ghp-import > /dev/null 2>&1 || {
	echo "ghp-import not found."
	echo "'pip install ghp-import' to install"
	exit 1
}

basedir=$(cd $(dirname $0)/../; pwd)
docdir="${basedir}/docs"
builddir="${docdir}/_build/html"
buildscript="${basedir}/bin/build-docs.sh"

echo "\$basedir  : ${basedir}"
echo "\$docdir   : ${docdir}"
echo "\$builddir : ${builddir}"

# cd "${docdir}"
# if [[ -d _build/html ]]; then
# 	rm -rf _build/html
# fi
# make html
# cd -

/bin/bash "${buildscript}"

echo "######################################################################"
echo "Publishing docs to gh-pages branch"
echo "######################################################################"

# Publish $builddir to gh-pages branch
ghp-import -n -p -m "$1" "${builddir}"

