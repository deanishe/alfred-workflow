#!/bin/bash
# check that magic args work and appropriate files/directories are opened

script=./_magic_args.py

$script workflow:openworkflow
$script workflow:opendata
$script workflow:opencache
$script workflow:openlog

