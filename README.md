
# Alfred-Workflow #

A helper library in Python for authors of workflows for [Alfred 2](http://www.alfredapp.com/).

[![Build Status](https://travis-ci.org/deanishe/alfred-workflow.svg?branch=master)](https://travis-ci.org/deanishe/alfred-workflow)
[![Coverage Status](https://img.shields.io/coveralls/deanishe/alfred-workflow.svg)](https://coveralls.io/r/deanishe/alfred-workflow?branch=master)
[![Latest Version](https://pypip.in/version/Alfred-Workflow/badge.svg?text=version)](https://pypi.python.org/pypi/Alfred-Workflow/)
[![Supported Python versions](https://pypip.in/py_versions/Alfred-Workflow/badge.svg)](https://pypi.python.org/pypi/Alfred-Workflow/)
[![License](https://pypip.in/license/Alfred-Workflow/badge.svg)](https://pypi.python.org/pypi/Alfred-Workflow/)

## Features ##

- Catches and logs workflow errors for easier development and support
- "Magic" arguments to help development/debugging
- Auto-saves settings
- Super-simple data caching
- Fuzzy, Alfred-like search/filtering with diacritic folding
- Keychain support for secure storage of passwords, API keys etc.
- Simple generation of Alfred feedback (XML output)
- Input/output decoding for handling non-ASCII text
- Lightweight web API with [Requests](http://docs.python-requests.org/en/latest/)-like interface
- Pre-configured logging
- Painlessly add directories to `sys.path`
- Easily launch background tasks (daemons) to keep your workflow responsive
- Check for new versions of and update workflows hosted on GitHub.

## Installation ##

### With pip ###

You can install **Alfred-Workflow** directly into your workflow with:

```bash
pip install --target=/path/to/my/workflow Alfred-Workflow
```

**Note**: If you intend to distribute your workflow to other users, you should
include **Alfred-Workflow** (and other Python libraries your workflow requires)
within your workflow as described. Do not ask users to install anything into
their system Python.

### From source ###

1. Download the `alfred-workflow-X.X.zip` from the [releases page](https://github.com/deanishe/alfred-workflow/releases).
2. Either extract the ZIP archive and place the `workflow` directory in the root folder of your workflow (where `info.plist` is) **or**
3. Place the ZIP archive in the root folder of your workflow and add `sys.path.insert(0, 'alfred-workflow-X.X.zip')` at the top of your Python script(s).

Your workflow should look something like this:

    Your Workflow/
        info.plist
        icon.png
        workflow/
            __init__.py
            background.py
            workflow.py
            web.py
        yourscript.py
        etc.

Or this:

    Your Workflow/
        info.plist
        icon.png
        workflow-1.X.X.zip
        yourscript.py
        etc.

**Note:** the `background.py` module will not work from within a zip archive.

Alternatively, you can clone/download the Alfred-Workflow [repository](https://github.com/deanishe/alfred-workflow) and copy the `workflow` subdirectory to your workflow's root directory.

## Usage ##

A few examples of how to use **Alfred-Workflow**.

### Workflow script skeleton ###

Set up your workflow scripts as follows (if you wish to use the built-in error handling or `sys.path` modification):

```python
#!/usr/bin/python
# encoding: utf-8

import sys

from workflow import Workflow


def main(wf):
    # The Workflow instance will be passed to the function
    # you call from `Workflow.run`
    # Your imports here if you want to catch import errors
    # or if the modules/packages are in a directory added via `Workflow(libraries=...)`
    import somemodule
    import anothermodule
    # Get args from Workflow, already in normalised Unicode
    args = wf.args

    # Do stuff here ...

    # Add an item to Alfred feedback
    wf.add_item(u'Item title', u'Item subtitle')

    # Send output to Alfred
    wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
```

### Examples ###

Cache data for 30 seconds:

```python
def get_web_data():
    return web.get('http://www.example.com').json()

def main(wf):
    # Save data from `get_web_data` for 30 seconds under
    # the key ``example``
    data = wf.cached_data('example', get_web_data, max_age=30)
    for datum in data:
        wf.add_item(datum['title'], datum['author'])
    wf.send_feedback()
```

#### Web ####

Grab data from a JSON web API:

```python
data = web.get('http://www.example.com/api/1/stuff').json()
```

Post a form:

```
r = web.post('http://www.example.com/', data={'artist': 'Tom Jones', 'song': "It's not unusual"})
```

Upload a file:

```
files = {'fieldname' : {'filename': "It's not unusual.mp3",
                        'content': open("It's not unusual.mp3", 'rb').read()}
}
r = web.post('http://www.example.com/upload/', files=files)
```

**WARNING**: As this module is based on Python 2's standard HTTP libraries, it *cannot* validate SSL certificates when making HTTPS connections. If your workflow uses sensitive passwords/API keys, you should *strongly consider* using the [requests](http://docs.python-requests.org/en/latest/) library upon which the `web.py` API is based.

#### Keychain access ####

Save password:

```python
wf = Workflow()
wf.save_password('name of account', 'password1lolz')
```

Retrieve password:

```python
wf = Workflow()
wf.get_password('name of account')
```

## Documentation ##

The full documentation, including auto-generated API docs and a tutorial, can be found [here](http://www.deanishe.net/alfred-workflow/).

## Licensing, thanks ##

The code and the documentation are released under the MIT and [Creative Commons Attribution-NonCommercial](https://creativecommons.org/licenses/by-nc/4.0/legalcode) licences respectively. See LICENSE for details.

The documentation was generated using [Sphinx](http://sphinx-doc.org/), [Sphinx Bootstrap Theme](http://ryan-roemer.github.io/sphinx-bootstrap-theme/), [Bootstrap](http://getbootstrap.com/) and the [Readable Bootswatch theme](http://bootswatch.com/readable/).

## Contributing ##

Bug reports, feature suggestions and pull requests are very welcome. Head over to the [issues](https://github.com/deanishe/alfred-workflow/issues) if you have a feature request or a bug report.

If you want to make a pull request, do that [here](https://github.com/deanishe/alfred-workflow/pulls), but please bear the following in mind:

- **Alfred-Workflow** has very close to 100% test coverage. The only code that isn't covered by unit/functional tests is the code that opens external applications. "Proof-of-concept" pull requests without tests are more than welcome. However, please be prepared to add the appropriate tests if you want your pull request to be ultimately accepted.
- Complete coverage is *only a proxy* for decent tests. Tests should also cover a decent variety of valid/invalid input. For example, if the code *could potentially* be handed non-ASCII input, it should be tested with non-ASCII input.
- Code should be [PEP8](http://legacy.python.org/dev/peps/pep-0008/)-compliant as far as is reasonable. Any decent code editor has a PEP8 plugin that will warn you of potential transgressions.
- Please choose your function, method and argument names carefully, with an eye to the existing names. Obviousness is more important than brevity.
- Document your code using the [Sphinx ReST format](http://sphinx-doc.org/). Even if your function/method isn't user-facing, some other developer will be looking at it. Even if it's only a one-liner, the developer may be looking at [the docs](http://www.deanishe.net/alfred-workflow/#api-docs) in a browser, not at the source code.
- Performance counts. Alfred will try to run a workflow anew on every keypress. As a rule, 0.3 seconds execution time is decent, 0.2 seconds or less is smooth. **Alfred-Workflow** should do its utmost to consume as little of that time as possible.

Currently, there is Travis-CI integration, but also a `run-tests.sh` script in the root directory of the repo which will fail *if code coverage is less than 100%* (Travis-CI also uses this script). Add `# pragma: no cover` with care.

### Contributors ###

- [Dean Jackson](https://github.com/deanishe)
- [Stephen Margheim](https://github.com/smargh)
- [Fabio Niephaus](https://github.com/fniephaus)

## Workflows using Alfred-Workflow ##

These are some of the Alfred workflows that use this library.

- [Alfred Backblaze](http://www.packal.org/workflow/alfred-backblaze) by [XedMada](http://www.packal.org/users/xedmada). Pause and Start Backblaze online backups.
- [Alfred Dependency Bundler Demo (Python)](http://www.packal.org/workflow/alfred-dependency-bundler-demo-python) by [deanishe](http://www.packal.org/users/deanishe). Demonstration on how to use the Alfred Bundler in Python.
- [AppScripts](http://www.packal.org/workflow/appscripts) by [deanishe](http://www.packal.org/users/deanishe). List, search and run/open AppleScripts for the active application.
- [BibQuery](http://www.packal.org/workflow/bibquery) by [hackademic](http://www.packal.org/users/hackademic). Search BibDesk from the comfort of your keyboard.
- [Blur](http://www.packal.org/workflow/blur) by [Tyler Eich](http://www.packal.org/users/tyler-eich). Set Alfred's background blur radius.
- [Convert](http://www.packal.org/workflow/convert) by [deanishe](http://www.packal.org/users/deanishe). Convert between different units. No Internet connection required.
- [Date Calculator](http://www.packal.org/workflow/date-calculator) by [MuppetGate](http://www.packal.org/users/muppetgate). A basic date calculator.
- [Digital Ocean status](http://www.packal.org/workflow/digital-ocean-status) by [frankspin](http://www.packal.org/users/frankspin). Check the status of your Digital Ocean droplets.
- [Display Brightness](http://www.packal.org/workflow/display-brightness) by [fniephaus](http://www.packal.org/users/fniephaus). Adjust your display's brightness with Alfred.
- [Dropbox Client for Alfred](http://www.packal.org/workflow/dropbox-client-alfred) by [fniephaus](http://www.packal.org/users/fniephaus). Access multiple Dropbox accounts with Alfred.
- [Duden Search](http://www.packal.org/workflow/duden-search) by [deanishe](http://www.packal.org/users/deanishe). Search duden.de German dictionary (with auto-suggest).
- [Fabric for Alfred](http://www.packal.org/workflow/fabric-alfred) by [fniephaus](http://www.packal.org/users/fniephaus). Quickly execute Fabric tasks.
- [Fuzzy Folders](http://www.packal.org/workflow/fuzzy-folders) by [deanishe](http://www.packal.org/users/deanishe). Fuzzy search across folder subtrees.
- [Git Repos](http://www.packal.org/workflow/git-repos) by [deanishe](http://www.packal.org/users/deanishe). Browse, search and open Git repositories from within Alfred.
- [Glosbe Translation](http://www.packal.org/workflow/glosbe-translation) by [deanishe](http://www.packal.org/users/deanishe). Translate text using Glosbe.com.
- [Homebrew for Alfred](http://www.packal.org/workflow/homebrew-alfred) by [fniephaus](http://www.packal.org/users/fniephaus). Easily control Homebrew with Alfred.
- [IPython Notebooks](http://www.packal.org/workflow/ipython-notebooks) by [nkeim](http://www.packal.org/users/nkeim). Search notebook titles on your IPython notebook server.
- [Laser SSH](http://www.packal.org/workflow/laser-ssh) by [paperElectron](http://www.packal.org/users/paperelectron). Choose SSH connection from filterable list.
- [LibGen](http://www.packal.org/workflow/libgen) by [hackademic](http://www.packal.org/users/hackademic). Search and Download pdfs and ebooks from Library Genesis.
- [Network Location](http://www.packal.org/workflow/network-location) by [deanishe](http://www.packal.org/users/deanishe). List, filter and activate network locations from within Alfred.
- [Packal Workflow Search](http://www.packal.org/workflow/packal-workflow-search) by [deanishe](http://www.packal.org/users/deanishe). Search Packal.org from the comfort of Alfred.
- [Pandoctor](http://www.packal.org/workflow/pandoctor) by [hackademic](http://www.packal.org/users/hackademic). An Alfred GUI for Pandoc.
- [Parsers](http://www.packal.org/workflow/parsers) by [hackademic](http://www.packal.org/users/hackademic). Greek and Latin parsers.
- [Pocket for Alfred](http://www.packal.org/workflow/pocket-alfred) by [fniephaus](http://www.packal.org/users/fniephaus). Manage your Pocket list with Alfred.
- [Quick Stocks](http://www.packal.org/workflow/quick-stocks) by [paperElectron](http://www.packal.org/users/paperelectron). Add some stock symbols for Alfred to check for you.
- [Readability for Alfred](http://www.packal.org/workflow/readability-alfred) by [fniephaus](http://www.packal.org/users/fniephaus). Manage your Readability list with Alfred.
- [Relative Dates](http://www.packal.org/workflow/relative-dates) by [deanishe](http://www.packal.org/users/deanishe). Generate relative dates based on a simple input format.
- [SEND](http://www.packal.org/workflow/send) by [hackademic](http://www.packal.org/users/hackademic). Send documents to the cloud.
- [Searchio!](http://www.packal.org/workflow/searchio) by [deanishe](http://www.packal.org/users/deanishe). Auto-suggest search results from multiple search engines and languages.
- [Skimmer](http://www.packal.org/workflow/skimmer) by [hackademic](http://www.packal.org/users/hackademic). Actions for PDF viewer Skim.
- [Snippets](http://www.packal.org/workflow/snippets) by [hackademic](http://www.packal.org/users/hackademic). Simple, document-specific text snippets.
- [Spritzr](http://www.packal.org/workflow/spritzr) by [hackademic](http://www.packal.org/users/hackademic). An Alfred Speed-Reader.
- [Sublime Text Projects](http://www.packal.org/workflow/sublime-text-projects) by [deanishe](http://www.packal.org/users/deanishe). View, filter and open your Sublime Text (2 and 3) project files.
- [Torrent](http://www.packal.org/workflow/torrent) by [bfw](http://www.packal.org/users/bfw). Search for torrents, choose among the results in Alfred and start the download in uTorrent.
- [Travis CI for Alfred](http://www.packal.org/workflow/travis-ci-alfred) by [fniephaus](http://www.packal.org/users/fniephaus). Quickly check build statuses on travis-ci.org.
- [VM Control](http://www.packal.org/workflow/vm-control) by [fniephaus](http://www.packal.org/users/fniephaus). Control your Parallels and Virtual Box virtual machines.
- [Wikify](http://www.packal.org/workflow/wikify) by [hackademic](http://www.packal.org/users/hackademic). Your little Evernote Wiki-Helper.
- [ZotQuery](http://www.packal.org/workflow/zotquery) by [hackademic](http://www.packal.org/users/hackademic). Search Zotero. From the Comfort of Your Keyboard.
