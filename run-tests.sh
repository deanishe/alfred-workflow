#!/bin/bash

rootdir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
logpath="${rootdir}/test.log"

function log() {
    echo "$@" | tee -a $logpath
}

# Delete old log file if it exists
if [[ -f "${logpath}" ]]; then
    rm -rf "${logpath}"
fi


# Set test options and run tests
#-------------------------------------------------------------------------

# Most options are in tox.ini
PYTEST_OPTS="--cov workflow"

log "Running tests..."

# nosetests $NOSETEST_OPTIONS 2>&1 | tee -a $logpath
py.test $PYTEST_OPTS 2>&1 | tee -a $logpath
ret=${PIPESTATUS[0]}

echo

case "$ret" in
    0) log -e "SUCCESS" ;;
    *) log -e "FAILURE" ;;
esac

if [[ "${ret}" -ne 0 ]]; then
	exit $ret
fi

# Test coverage
coverage report --fail-under 100 --show-missing
ret=${PIPESTATUS[0]}

echo

case "$ret" in
    0) log -e "SUCCESS" ;;
    *) log -e "FAILURE" ;;
esac

exit $ret
