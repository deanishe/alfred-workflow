#!/bin/bash
rootdir="$( cd "$( dirname "$0" )"; pwd )"

usage() {
  cat > /dev/stderr <<EOS
run-tests.sh [-v|-V] [-c <pkg>] [<tests/test_script.py>...]

Run test script(s) with coverage for one package.

Usage:
    run-tests.sh [-v|-V] [-c <pkg>] [-l] [-t] [<tests/test_script.py>...]
    run-tests.sh -h

Options:
    -c <pkg>  coverage report package
    -l        run linter
    -t        run tests (default)
    -v        verbose output
    -V        very verbose output
    -h        show this message and exit

Example:
    run-tests.sh -c workflow.notify tests/test_notify.py

EOS
}

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

coverpkg=workflow
vopts=
dolint=1
dotest=0
forcetest=1
while getopts ":c:hltvVx" opt; do
  case $opt in
    c)
      coverpkg="$OPTARG"
      PYTEST_ADDOPTS="$PYTEST_ADDOPTS --cov-report=html --cov="$coverpkg""
      ;;
    l)
      dolint=0
      ;;
    t)
      forcetest=0
      ;;
    h)
      usage
      exit 0
      ;;
    v)
      vopts="-v"
      ;;
    x)
      PYTEST_ADDOPTS="$PYTEST_ADDOPTS --last-failed --last-failed-no-failures all"
      ;;
    V)
      vopts="-vv"
      ;;
    \?)
      log "Invalid option: -$OPTARG"
      exit 1
      ;;
  esac
done
shift $((OPTIND-1))

# Set test options and run tests
#-------------------------------------------------------------------------

unset alfred_version alfred_workflow_version alfred_workflow_bundleid
unset alfred_workflow_name alfred_workflow_cache alfred_workflow_data

files=(tests)
if [[ $# -gt 0 ]]; then
  files=$@
fi

if [[ "$dolint" -eq 0 ]]; then
  dotest=1
fi

if [[ "$forcetest" -eq 0 ]]; then
  dotest=0
fi

coverage erase
# command rm -fv .coverage.*

if [[ $dotest -eq 0 ]]; then
  # More options are in tox.ini

  export PYTEST_ADDOPTS
  export PYTEST_RUNNING=1
  python3 -m pytest $vopts -vv tests "$@" 
  ret1=${PIPESTATUS[0]}
  echo

  case "$ret1" in
      0) success "TESTS OK" ;;
      *) fail "TESTS FAILED" ;;
  esac
  if [[ "$ret1" -ne 0 ]]; then
    exit $ret1
  fi
  echo
fi


if [[ $dolint -eq 0 ]]; then
  flake8 $files
  ret2=${PIPESTATUS[0]}

  case "$ret2" in
      0) success "LINTING OK" ;;
      *) fail "LINTING FAILED" ;;
  esac
fi

if [[ "$ret2" -ne 0 ]]; then
  exit $ret2
fi

if [[ "$dotest" -eq 1 ]]; then
  exit 0
fi

# Test coverage
# coverage xml
# coverage report --fail-under 100 --show-missing
# ret3=${PIPESTATUS[0]}

# echo

# case "$ret3" in
#     0) success "COVERAGE OK" ;;
#     *) fail "COVERAGE FAILED" ;;
# esac

# exit $ret3
