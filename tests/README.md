
Test suite
==========

Unit tests and data for Alfred-Workflow. Currently an unholy mix of `unittest` and `py.test` (moving towards the latter).


Running the full suite with coverage
------------------------------------

```bash
./run-tests.sh
```
in the project root to run the full test suite in place with coverage.

```bash
tox
```
in the project root to build, install and test with Python.


Testing a single module with coverage
-------------------------------------

```bash
extras/testone <module.name> <tests/test_script.py>...
```

to run test script(s) with coverage for a single module.
