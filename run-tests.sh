#!/bin/bash
# Copied from flask-login
# https://github.com/maxcountryman/flask-login

# OUTPUT_PATH=$(pwd)/tests_output

rootdir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
workflow="${rootdir}/workflow"
logpath="${rootdir}/test.log"
testroot="/tmp/alfred-wörkflöw-$$"
testdir="${testroot}/tests"
curdir=$(pwd)

function log() {
    echo "$@" | tee -a $logpath
}

# Delete old log file if it exists
if [[ -f "${logpath}" ]]; then
    rm -rf "${logpath}"
fi

###############################################################################
# Set up test environment
###############################################################################
if [[ -d "${testroot}" ]]; then
    rm -rf "${testroot}"
fi

mkdir -p "${testroot}"
cp -R "${rootdir}/tests" "${testdir}"
ln -s "${rootdir}/workflow" "${testdir}/workflow"
ln -s "${rootdir}/tests/info.plist.test" "${testroot}/info.plist"

cd "${testdir}"


###############################################################################
# Set test options and run tests
###############################################################################

NOSETEST_OPTIONS="-d"

if [ -n "$VERBOSE" ]; then
    NOSETEST_OPTIONS="$NOSETEST_OPTIONS --verbose"
fi

if [ -z "$NOCOLOR" ]; then
    NOSETEST_OPTIONS="$NOSETEST_OPTIONS --with-yanc --yanc-color=on"
fi

if [ -n "$OPTIONS" ]; then
    NOSETEST_OPTIONS="$NOSETEST_OPTIONS $OPTIONS"
fi

if [ -n "$TESTS" ]; then
    NOSETEST_OPTIONS="$NOSETEST_OPTIONS $TESTS"
else
    NOSETEST_OPTIONS="$NOSETEST_OPTIONS -v --with-coverage --cover-min-percentage=100 --cover-package=workflow --logging-clear-handlers"
fi

log "Running tests..."

nosetests $NOSETEST_OPTIONS 2>&1 | tee -a $logpath
ret=${PIPESTATUS[0]}

echo

case "$ret" in
    0) log -e "SUCCESS" ;;
    *) log -e "FAILURE" ;;
esac

###############################################################################
# Delete test environment
###############################################################################

cd "$curdir"

if [[ -d "${testroot}" ]]; then
    rm -rf "${testroot}"
fi

exit $ret
