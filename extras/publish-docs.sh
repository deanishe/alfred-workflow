#!/bin/bash

# Publish documentation to alfred-workflow-docs "sister" repo

if test -z "$1"
    then
        echo "You must specify a commit message."
        exit 1
fi

basedir=$(cd $(dirname $0)/../; pwd)
docdir="${basedir}/docs"
testdir="${basedir}/tests"
pubdir=$(cd $(dirname $0)/../../; pwd)/alfred-workflow-docs

echo "basedir : ${basedir}"
echo "docdir : ${docdir}"
echo "pubdir : ${pubdir}"

# info_linked=0

# if [[ ! -f "info.plist" ]]; then
# 	# link info.plist to parent directory so `background.py` can find it
# 	ln -s "${testdir}/info.plist.test" "${basedir}/info.plist"
# 	info_linked=1
# fi


cd "${docdir}"
if [[ -d _build/html ]]; then
	rm -rf _build/html
fi
make html
cp -R _build/html/* "${pubdir}/"
cd "${pubdir}"
git add .
git commit -m "$1"
git push origin gh-pages
cd "${basedir}"

# if [[ $info_linked -eq 1 ]]; then
# 	rm -f "${basedir}/info.plist"
# fi
