#!/bin/bash

rootdir="$( cd "$( dirname "$0" )"; pwd )"

if [ -t 1 ]; then
  red='\033[0;31m'
  green='\033[0;32m'
  nc='\033[0m'
else
  red=
  green=
  nc=
fi

function log() {
    echo "$@"
}

function fail() {
  printf "${red}$@${nc}\n"
}

function success() {
  printf "${green}$@${nc}\n"
}


# Set test options and run tests
#-------------------------------------------------------------------------

unset alfred_version alfred_workflow_version alfred_workflow_bundleid
unset alfred_workflow_name alfred_workflow_cache alfred_workflow_data

# More options are in tox.ini
export PYTEST_ADDOPTS="--cov-report=html"
pytest --cov=workflow tests

ret1=${PIPESTATUS[0]}

echo

case "$ret1" in
    0) success "TESTS OK" ;;
    *) fail "TESTS FAILED" ;;
esac

log ""


# Test coverage
coverage report --fail-under 100 --show-missing
ret2=${PIPESTATUS[0]}

echo

case "$ret2" in
    0) success "COVERAGE OK" ;;
    *) fail "COVERAGE FAILED" ;;
esac

test -z "$TRAVIS" && coverage erase

if [[ "$ret1" -ne 0 ]]; then
  exit $ret1
fi

exit $ret2
