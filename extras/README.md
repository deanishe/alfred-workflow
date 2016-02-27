
Extras
======

Helper scripts, icons and other stuff.


Build & distribution
--------------------

- `build-workflow.sh` — Build the distributable workflow as `workflow-1.n.n.zip` in the project root directory.
- `Notify.app` — AppleScript application to post notifications.
- `Notify.tgz` — The app compressed for distribution.
- `publish-cheeseshop.sh` — Build the distribution and publish on PyPi.
- `testone` — Run test script(s) with coverage for one module/package.
- `travis-install-deps.sh` — Install Python dependencies when running on [Travis CI][travis].


Docs
----

- `build-dash-docset.sh` — Build a docset for [Dash][dash] in `docs/` from HTML docs.
- `build-docs.sh` — Generate HTML docs in `docs/_build/html/`. You must run this before running `build-dash-docset.sh`.
- `gen_icon_table.py` — Generate the ReST table of system icons for the User Manual. Also generates PNGs in the `docs/_static/` directory.
- `generate_workflow_list.py` — Generate a Markdown/ReST list of workflows based on Alfred-Workflow from the Packal repository.
- `library_workflows.tsv` — Non-Packal workflows to include in the workflow list.
- `publish-docs.sh` — Build the docs and push them to `gh-pages` / http://www.deanishe.net/alfred-workflow/


Icons
-----

- `icons` — Generated and source files for the Alfred-Workflow icon.
	- `Alfred-Workflow.icns` — Generated Alfred-Workflow icon.
	- `Alfred-Workflow.iconset` — Generated Alfred-Workflow icon set.
	- `Alfred-Workflow.iconsproj` — Alfred-Workflow icon ICNS project file.
	- `Alfred-Workflow.png` — Generated Alfred-Workflow icon.
	- `Alfred-Workflow.sketch` — Alfred-Workflow icon source file.


[dash]: https://kapeli.com/dash
[travis]: https://travis-ci.org/deanishe/alfred-workflow
