#!/bin/bash

# rootdir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
rootdir="$( cd "$( dirname "$0" )"; pwd )"
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
PYTEST_OPTS="--cov workflow --cov-report html --cov-config=.coveragerc"

log "Running tests..."

py.test $PYTEST_OPTS tests 2>&1 | tee -a $logpath
ret1=${PIPESTATUS[0]}

echo

case "$ret1" in
    0) log "TESTS OK" ;;
    *) log "TESTS FAILED" ;;
esac

log ""

# if [[ "${ret}" -ne 0 ]]; then
#   exit $ret
# fi

# Test coverage
coverage report --fail-under 100 --show-missing
ret2=${PIPESTATUS[0]}

echo

case "$ret2" in
    0) log "COVERAGE OK" ;;
    *) log "COVERAGE FAILED" ;;
esac

if [[ "$ret1" -ne 0 ]]; then
  exit $ret1
fi

exit $ret2
