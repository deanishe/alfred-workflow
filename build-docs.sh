#!/bin/bash

basedir=$(cd $(dirname $0); pwd)
docdir="${basedir}/doc"
testdir="${basedir}/tests"
curdir=$(pwd)

info_linked=0

if [[ ! -f "info.plist" ]]; then
	# link info.plist to parent directory so `background.py` can find it
	ln -s "${testdir}/info.plist.test" "${basedir}/info.plist"
	info_linked=1
fi

cd "${docdir}"
if [[ -d _build/html ]]; then
	rm -rf _build/html
fi
make html
cd "${curdir}"


if [[ $info_linked -eq 1 ]]; then
	rm -f "${basedir}/info.plist"
fi
