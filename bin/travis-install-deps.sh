#!/bin/bash
# Install Python dependencies for Travis-CI.org

set -e

log() {
  echo "$@" > /dev/stderr
}

export CC=clang

log "----------------- Test dependencies ----------------"
pip install \
  pytest \
  coveralls \
  codacy-coverage \
  pytest_cov \
  pytest_httpbin \
  pytest_localserver

if [[ "$VERSION" =~ ^2.7.* ]]; then
  log "----------------------- PyObc ----------------------"
  pip install pyobjc-core
  pip install pyobjc-framework-Cocoa
fi

log "---------------------- Done ------------------------"
