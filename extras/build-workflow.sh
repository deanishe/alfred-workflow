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
zip-workflow.sh

Create distributable, useable ZIP archive of workflow in repo root.

Resulting file will be called workflow-1.n.n.zip

Usage:
	zip-workflow.sh [-s]
	zip-workflow.sh (-h|--help)

Options:
  zip-workflow.sh -s, --show	Only show what would be done.
  zip-workflow.sh -h, --help	Show this message and exit.

EOS
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

pushd "${rootdir}" &> /dev/null

if [[ -f "${zipfile}" ]] && [[ $show -eq 0 ]]; then
	log "Deleting existing zip archive"
	rm -f "${zipfile}"
fi


if [[ $show -eq 1 ]]; then
	mode="-sf"
else
	mode=
fi

# If there are Workflow Environment Variables with "Don't Export", make copy of workflow first and empty variables before packaging
if /usr/libexec/PlistBuddy -c 'Print variablesdontexport' "${sourcedir}/info.plist" &> /dev/null; then
	dirtopackage="$(mktemp -d)"
	cp -R "${sourcedir}/"* "${dirtopackage}"

	tmpinfoplist="${dirtopackage}/info.plist"
	/usr/libexec/PlistBuddy -c 'Print variablesdontexport' "${tmpinfoplist}" | grep '    ' | sed -E 's/ {4}//' | xargs -I {} /usr/libexec/PlistBuddy -c "Set variables:'{}' ''" "${tmpinfoplist}"
else
	dirtopackage="${sourcedir}"
fi

zip $mode -r ${zipfile} ${dirtopackage} -i $patterns

log "Created ${zipfile}"
popd &> /dev/null

exit 0
