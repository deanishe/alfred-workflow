#!/bin/bash

rootdir=$(cd $(dirname $0)/../; pwd)
version=$(cat "${rootdir}/workflow/version")
zipfile="alfred-workflow-${version}.zip"
sourcedir="workflow"

function help() {
cat << EOF
Create ZIP archive of workflow

  zip-workflow.sh -s, --show	Only show what would done
  zip-workflow.sh -h, --help	Show this message

EOF
}

show=0

case "$1" in
	-h|--help)
		help
		exit 0
		;;
	-s|--show)
		show=1
		;;
	*)
		;;
esac

cd "${rootdir}"

if [[ -f "${zipfile}" ]] && [[ $show -eq 0 ]]; then
	echo "Deleting existing zip archive"
	rm -f "${zipfile}"
fi


if [[ $show -eq 1 ]]; then
	zip -sf -r ${zipfile} ${sourcedir} -i '*.py'
	zip -sf -r ${zipfile} ${sourcedir} -i '*version'
	status=$?
else
	zip -r ${zipfile} ${sourcedir} -i '*.py' 'version'
	zip -r ${zipfile} ${sourcedir} -i '*version'
	status=$?
fi

if [[ $status -gt 0 ]]; then
	echo "ERROR: zip returned ${status}"
	exit $status
else
	if [[ $show -eq 0 ]]; then
		echo "Created ${zipfile}"
	fi
fi

cd -
