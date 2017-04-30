
bin
===

Scripts for building and publishing Alfred-Workflow.

- `build-workflow.sh` — Build the distributable workflow as `workflow-1.n.n.zip` in the project root directory.
- `publish-cheeseshop.sh` — Build the distribution and publish on PyPi.
- `build-dash-docset.sh` — Build a docset for [Dash][dash] in `docs/` from HTML docs.
- `build-docs.sh` — Generate HTML docs in `docs/_build/html/`. You must run this before running `build-dash-docset.sh`.
- `publish-docs.sh` — Build the docs and push them to `gh-pages` / http://www.deanishe.net/alfred-workflow/
- `testone` — Run test script(s) with coverage for one module/package.

[dash]: https://kapeli.com/dash
