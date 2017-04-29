#!/bin/zsh
# Create a useable, zipped version of the workflow in the repo root.
# The file will be named `alfred-workflow-X.X.X.zip`, or the like.

set -e

# Files to include in the zipped file
patterns=('workflow/*.py')
patterns+=('workflow/version')
patterns+=('workflow/Notify.tgz')

# Compute required paths relative to this script's location
# (i.e. Don't move this script without editing it)
rootdir=$(cd $(dirname $0)/../; pwd)
version=$(cat "${rootdir}/workflow/version")
zipfile="alfred-workflow-${version}.zip"
sourcedir="workflow"

log() {
	echo "$@" > /dev/stderr
}

help() {
cat > /dev/stderr << EOS
build-workflow.sh

Create distributable, useable ZIP archive of workflow in repo root.

Resulting file will be called workflow-1.n.n.zip

Usage:
	build-workflow.sh [-n]
	build-workflow.sh (-h|--help)

Options:
  -n, --nothing   Only show what would be done.
  -h, --help      Show this message and exit.

EOS
}

dryrun=0

case "$1" in
	-h|--help)
		help
		exit 0
		;;
	-n|--nothing)
		dryrun=1
		;;
	*)
		;;
esac

pushd "${rootdir}" &> /dev/null

if [[ -f "${zipfile}" ]] && [[ $dryrun -eq 0 ]]; then
	log "Deleting existing zip archive"
	rm -f "${zipfile}"
fi

mode=
if [[ $dryrun -eq 1 ]]; then
	mode="-sf"
fi

zip $mode -r ${zipfile} ${sourcedir} -i $patterns

log "Created ${zipfile}"
popd &> /dev/null

exit 0
