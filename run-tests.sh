#!/bin/bash

rootdir="$( cd "$( dirname "$0" )"; pwd )"

function log() {
    echo "$@" > /dev/stderr
}


# Set test options and run tests
#-------------------------------------------------------------------------

# More options are in tox.ini

export PYTEST_ADDOPTS="--cov-report=html"

log "Running tests..."

py.test --cov=workflow tests
ret1=${PIPESTATUS[0]}

echo

case "$ret1" in
    0) log "TESTS OK" ;;
    *) log "TESTS FAILED" ;;
esac

log ""


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
