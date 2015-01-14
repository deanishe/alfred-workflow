
# Alfred-Workflow #

A helper library in Python for authors of workflows for [Alfred 2][alfred].

[![Build Status][shield-travis]][travis]
[![Coverage Status][shield-coveralls]][coveralls]
[![Code Health][shield-health]][landscape]
[![Latest Version][shield-version]][pypi]
[![Development Status][shield-status]][pypi]
[![Documentation Status][shield-docs]][docs]
[![License][shield-licence]][pypi]
[![Downloads][shield-download]][pypi]


## Features ##

- Catches and logs workflow errors for easier development and support
- "Magic" arguments to help development/debugging
- Auto-saves settings
- Super-simple data caching
- Fuzzy, Alfred-like search/filtering with diacritic folding
- Keychain support for secure storage of passwords, API keys etc.
- Simple generation of Alfred feedback (XML output)
- Input/output decoding for handling non-ASCII text
- Lightweight web API with [Requests][requests]-like interface
- Pre-configured logging
- Painlessly add directories to `sys.path`
- Easily launch background tasks (daemons) to keep your workflow responsive
- Check for new versions and update workflows hosted on GitHub.

## Contents ##

- [Installation](#installation)
    - [With pip](#with-pip)
    - [ From source](#from-source)
- [Usage](#usage)
    - [Workflow script skeleton](#workflow-script-skeleton)
    - [Examples](#examples)
        - [Web](#web)
        - [Keychain access](#keychain-access)
- [Documentation](#documentation)
- [Licensing, thanks](#licensing-thanks)
- [Contributing](#contributing)
    - [Adding a workflow to the list](#adding-a-workflow-to-the-list)
    - [Bug reports, pull requests](#bug-reports-pull-requests)
    - [Contributors](#contributors)
- [Tests](#tests)
- [Workflows using Alfred-Workflow](#workflows-using-alfred-workflow)


## Installation ##

**Note**: If you intend to distribute your workflow to other users, you should
include Alfred-Workflow (and other Python libraries your workflow requires)
within your workflow's directory as described below. **Do not** ask users to
install anything into their system Python. Python installations cannot support
multiple versions of the same library, so if you rely on globally-installed
libraries, the chances are very good that your workflow will sooner or later
break—or be broken by—some other software doing the same naughty thing.

### With pip ###

You can install Alfred-Workflow directly into your workflow with:

```bash
pip install --target=/path/to/my/workflow Alfred-Workflow
```

You can install any other library available on the [Cheese Shop][cheeseshop] the same way. See the [pip documentation][pip-docs] for more information.

### From source ###

1. Download the `alfred-workflow-X.X.X.zip` from the
   [releases page][releases].
2. Either extract the ZIP archive and place the `workflow` directory in the
   root folder of your workflow (where `info.plist` is) **or**
3. Place the ZIP archive in the root folder of your workflow and add
   `sys.path.insert(0, 'alfred-workflow-X.X.X.zip')` at the top of your Python
   script(s).

Your workflow should look something like this:

    Your Workflow/
        info.plist
        icon.png
        workflow/
            __init__.py
            background.py
            update.py
            version
            web.py
            workflow.py
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

Alternatively, you can clone/download the Alfred-Workflow
[repository][repo] and copy the
`workflow` subdirectory to your workflow's root directory.

## Usage ##

A few examples of how to use Alfred-Workflow.

### Workflow script skeleton ###

Set up your workflow scripts as follows (if you wish to use the built-in error
handling or `sys.path` modification):

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

```python
r = web.post('http://www.example.com/', data={'artist': 'Tom Jones', 'song': "It's not unusual"})
```

Upload a file:

```python
files = {'fieldname' : {'filename': "It's not unusual.mp3",
                        'content': open("It's not unusual.mp3", 'rb').read()}
}
r = web.post('http://www.example.com/upload/', files=files)
```

**WARNING**: As this module is based on Python 2's standard HTTP libraries, it
*cannot* validate SSL certificates when making HTTPS connections. If your
workflow uses sensitive passwords/API keys, you should *strongly consider*
using the [requests][requests] library upon which the `web.py` API is based.

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

The full documentation, including API docs and a tutorial, can be found
[here][docs].

There is a mirror at [Read the Docs][docs-rtd].

## Licensing, thanks ##

The code and the documentation are released under the MIT and
[Creative Commons Attribution-NonCommercial][cc]
licences respectively. See [LICENCE.txt](LICENCE.txt) for details.

The documentation was generated using [Sphinx][sphinx] using
the [Read the Docs][rtd] theme.

## Contributing ##

### Adding a workflow to the list ###

If you want to add a workflow to the
[list of workflows using Alfred-Workflow](#workflows-using-alfred-workflow),
**don't add it to this README!** The list is automatically generated from
[Packal.org][packal] and the
[`library_workflows.tsv`](extras/library_workflows.tsv) file. If your workflow
is available on [Packal][packal], it should be added automatically. If not,
please add it to [`library_workflows.tsv`](extras/library_workflows.tsv),
instead of `README.md`, and submit a corresponding pull request.

### Bug reports, pull requests ###

Bug reports, feature suggestions and pull requests are very welcome. Head over
to the [issues][issues] if you have a feature request or a bug report.

If you want to make a pull request, do that [here][pulls], but please bear
the following in mind:

- Please open pull requests against the `develop` branch. I try to keep
  `master` in sync with the latest release (at least regarding any files
  included in releases). `master` and `develop` are *usually* in sync, but
  if I'm working on new features, they'll be in `develop` and won't be pushed
  to `master` until they're ready for release.
- Alfred-Workflow has very close to 100% test coverage. "Proof-of-concept"
  pull requests without tests are more than welcome. However, please be
  prepared to add the appropriate tests if you want your pull request to be
  ultimately accepted.
- Complete coverage is *only a proxy* for decent tests. Tests should also
  cover a decent variety of valid/invalid input. For example, if the code
  *could potentially* be handed non-ASCII input, it should be tested with
  non-ASCII input.
- Code should be [PEP8][pep8]-compliant as far as is reasonable. Any decent
  code editor has a PEP8 plugin that will warn you of potential transgressions.
- Please choose your function, method and argument names carefully, with an
  eye to the existing names. Obviousness is more important than brevity.
- Document your code using the [Sphinx ReST format][sphinx].
  Even if your function/method isn't user-facing, some other developer will be
  looking at it. Even if it's only a one-liner, the developer may be looking
  at [the docs][docs-api] in a browser, not at the source code.
- Performance counts. Alfred will try to run a workflow anew on every
  keypress. As a rule, 0.3 seconds execution time is decent, 0.2 seconds or
  less is smooth. Alfred-Workflow should do its utmost to consume as
  little of that time as possible.

Currently, there is Travis-CI integration, but also a `run-tests.sh` script in
the root directory of the repo which will fail *if code coverage is less than
100%* (Travis-CI also uses this script). Add `# pragma: no cover` with care.

### Contributors ###

- [Dean Jackson][deanishe]
- [Stephen Margheim][smargh]
- [Fabio Niephaus][fniephaus]
- [Owen Min][owenwater]

## Tests ##

Alfred-Workflow includes a full suite of unit tests. Please use the
`run-tests.sh` script in the root directory of the repo to run the unit tests:
it creates the necessary test environment to run the unit tests.
`test_workflow.py` *will* fail if not run via `run-scripts.sh`, but the test
suites for the other modules may also be run directly.

Moreover, `run-tests.sh` checks the coverage of the unit tests and will fail if
it is below 100%.

## Workflows using Alfred-Workflow ##

These are some of the Alfred workflows that use this library.

Updating edc1d2a..7e87144
Fast-forward
 .../appcast.xml                                    |   9 +
 .../hostelworld-search.alfredworkflow              | Bin 0 -> 229024 bytes
 com.bachya.lpvm/appcast.xml                        |   9 +
 .../lastpass_vault_manager.alfredworkflow          | Bin 0 -> 159345 bytes
 com.calebevans.playsong/appcast.xml                |   6 +-
 com.calebevans.playsong/play_song.alfredworkflow   | Bin 105358 -> 105235 bytes
 .../alfrededitor.alfredworkflow                    | Bin 0 -> 1278573 bytes
 com.customct.AlfredEditor/appcast.xml              |   9 +
 com.customct.CopyMoveWorkflow/appcast.xml          |   6 +-
 .../copy-moveto.alfredworkflow                     | Bin 16369 -> 17347 bytes
 com.customct.FoldingTextWorkflow/appcast.xml       |   6 +-
 .../foldingtextworkflow.alfredworkflow             | Bin 111523 -> 120948 bytes
 com.customct.Mjolnir/appcast.xml                   |   6 +-
 .../mjolnirworkflow.alfredworkflow                 | Bin 32240 -> 37255 bytes
 com.customct.TextWell/appcast.xml                  |   9 +
 .../textwellworkflow.alfredworkflow                | Bin 0 -> 35414 bytes
 com.customct.hammerspoon/appcast.xml               |   9 +
 .../hammerspoonworkflow.alfredworkflow             | Bin 0 -> 43487 bytes
 com.davidberube.trello-alfred/appcast.xml          |   9 +
 .../trello.alfredworkflow                          | Bin 0 -> 124123 bytes
 com.fniephaus.pocket/appcast.xml                   |   6 +-
 .../pocket-for-alfred.alfredworkflow               | Bin 49281 -> 54753 bytes
 com.jason0x43.alfred-hue/alfred-hue.alfredworkflow | Bin 2027963 -> 2078530 bytes
 com.jason0x43.alfred-hue/appcast.xml               |   6 +-
 .../alfred-toggl.alfredworkflow                    | Bin 1618956 -> 1688819 bytes
 com.jason0x43.alfred-toggl/appcast.xml             |   6 +-
 com.kejadlen.forecast/appcast.xml                  |   6 +-
 com.kejadlen.forecast/forecast.alfredworkflow      | Bin 103900 -> 103962 bytes
 .../appcast.xml                                    |   9 +
 .../markdown_note_of_github_repo.alfredworkflow    | Bin 0 -> 11234 bytes
 com.mcknight.movies/appcast.xml                    |   9 +
 com.mcknight.movies/movies.alfredworkflow          | Bin 0 -> 1112398 bytes
 com.robertwdempsey.flux/appcast.xml                |   9 +
 com.robertwdempsey.flux/f.lux_.alfredworkflow      | Bin 0 -> 7680 bytes
 com.satyavolu.alfred.hunterdouglas/appcast.xml     |   9 +
 .../hunter_douglas_platinum_control.alfredworkflow | Bin 0 -> 65542 bytes
 com.vitorgalvao.alfred.runcommand/appcast.xml      |   6 +-
 .../runcommand.alfredworkflow                      | Bin 7274 -> 7470 bytes
 fspinillo.alfredv2.digitalocean/appcast.xml        |   4 +-
 .../digital_ocean_status.alfredworkflow            | Bin 928817 -> 927582 bytes
 fspinillo.alfredv2.slackfred/appcast.xml           |   4 +-
 .../slackfred.alfredworkflow                       | Bin 296426 -> 296595 bytes
 info.oddgeek.bard/appcast.xml                      |   9 +
 .../shakespearean_insult_generator.alfredworkflow  | Bin 0 -> 860456 bytes
 manifest.xml                                       | 338 ++++++++++++++++++---
 muppet.gate.net.DateCalculator/appcast.xml         |   8 +-
 ...fredworkflow => date_calculator.alfredworkflow} | Bin 410105 -> 492565 bytes
 net.deanishe.alfred-convert/appcast.xml            |   6 +-
 net.deanishe.alfred-convert/convert.alfredworkflow | Bin 233086 -> 237717 bytes
 net.deanishe.alfred-fakeum/appcast.xml             |   9 +
 .../fakeum-1.1.alfredworkflow                      | Bin 0 -> 420557 bytes
 net.deanishe.alfred-git-repos/appcast.xml          |   6 +-
 .../git_repos.alfredworkflow                       | Bin 222351 -> 248697 bytes
 net.deanishe.alfred-reddit/appcast.xml             |   9 +
 .../reddit-1.2.alfredworkflow                      | Bin 0 -> 73125 bytes
 net.deanishe.alfred-searchio/appcast.xml           |   8 +-
 ....alfredworkflow => searchio-1.5.alfredworkflow} | Bin 598758 -> 622169 bytes
 net.deanishe.alfred-stackoverflow/appcast.xml      |   9 +
 .../stackoverflow-1.1.alfredworkflow               | Bin 0 -> 86964 bytes
 net.exit4web.hash/appcast.xml                      |   9 +
 net.exit4web.hash/hash.alfredworkflow              | Bin 0 -> 25689 bytes
 net.guiguan.Uni-Call/appcast.xml                   |   8 +-
 net.guiguan.Uni-Call/uni-call.alfredworkflow       | Bin 800576 -> 0 bytes
 net.guiguan.Uni-Call/uni_call.alfredworkflow       | Bin 0 -> 4479853 bytes
 so.muk.wishket/appcast.xml                         |   8 +-
 so.muk.wishket/wishket_search-1.1.alfredworkflow   | Bin 161398 -> 0 bytes
 so.muk.wishket/wishket_search-1.2.alfredworkflow   | Bin 0 -> 946624 bytes
 zmin.calendar/appcast.xml                          |   9 +
 zmin.calendar/calendar.alfredworkflow              | Bin 0 -> 44526 bytes
 zmin.forvo/appcast.xml                             |   9 +
 zmin.forvo/forvo.alfredworkflow                    | Bin 0 -> 50440 bytes
 71 files changed, 495 insertions(+), 102 deletions(-)
 create mode 100644 cat.claudi.alfredworkflow.hostelworld.search/appcast.xml
 create mode 100644 cat.claudi.alfredworkflow.hostelworld.search/hostelworld-search.alfredworkflow
 create mode 100644 com.bachya.lpvm/appcast.xml
 create mode 100644 com.bachya.lpvm/lastpass_vault_manager.alfredworkflow
 create mode 100644 com.customct.AlfredEditor/alfrededitor.alfredworkflow
 create mode 100644 com.customct.AlfredEditor/appcast.xml
 create mode 100644 com.customct.TextWell/appcast.xml
 create mode 100644 com.customct.TextWell/textwellworkflow.alfredworkflow
 create mode 100644 com.customct.hammerspoon/appcast.xml
 create mode 100644 com.customct.hammerspoon/hammerspoonworkflow.alfredworkflow
 create mode 100644 com.davidberube.trello-alfred/appcast.xml
 create mode 100644 com.davidberube.trello-alfred/trello.alfredworkflow
 create mode 100644 com.lastobelus.alfred.markdown-note-of-github-repo/appcast.xml
 create mode 100644 com.lastobelus.alfred.markdown-note-of-github-repo/markdown_note_of_github_repo.alfredworkflow
 create mode 100644 com.mcknight.movies/appcast.xml
 create mode 100644 com.mcknight.movies/movies.alfredworkflow
 create mode 100644 com.robertwdempsey.flux/appcast.xml
 create mode 100644 com.robertwdempsey.flux/f.lux_.alfredworkflow
 create mode 100644 com.satyavolu.alfred.hunterdouglas/appcast.xml
 create mode 100644 com.satyavolu.alfred.hunterdouglas/hunter_douglas_platinum_control.alfredworkflow
 create mode 100644 info.oddgeek.bard/appcast.xml
 create mode 100644 info.oddgeek.bard/shakespearean_insult_generator.alfredworkflow
 rename muppet.gate.net.DateCalculator/{datecalculator.alfredworkflow => date_calculator.alfredworkflow} (70%)
 create mode 100644 net.deanishe.alfred-fakeum/appcast.xml
 create mode 100644 net.deanishe.alfred-fakeum/fakeum-1.1.alfredworkflow
 create mode 100644 net.deanishe.alfred-reddit/appcast.xml
 create mode 100644 net.deanishe.alfred-reddit/reddit-1.2.alfredworkflow
 rename net.deanishe.alfred-searchio/{searchio.alfredworkflow => searchio-1.5.alfredworkflow} (90%)
 create mode 100644 net.deanishe.alfred-stackoverflow/appcast.xml
 create mode 100644 net.deanishe.alfred-stackoverflow/stackoverflow-1.1.alfredworkflow
 create mode 100644 net.exit4web.hash/appcast.xml
 create mode 100644 net.exit4web.hash/hash.alfredworkflow
 delete mode 100644 net.guiguan.Uni-Call/uni-call.alfredworkflow
 create mode 100644 net.guiguan.Uni-Call/uni_call.alfredworkflow
 delete mode 100644 so.muk.wishket/wishket_search-1.1.alfredworkflow
 create mode 100644 so.muk.wishket/wishket_search-1.2.alfredworkflow
 create mode 100644 zmin.calendar/appcast.xml
 create mode 100644 zmin.calendar/calendar.alfredworkflow
 create mode 100644 zmin.forvo/appcast.xml
 create mode 100644 zmin.forvo/forvo.alfredworkflow
- [Alfred Backblaze](http://www.packal.org/workflow/alfred-backblaze)
  ([GitHub repo](https://github.com/XedMada/alfred-backblaze))
  by [XedMada](http://www.packal.org/users/xedmada)
  ([on GitHub](https://github.com/XedMada/)).
  Pause and Start Backblaze online backups.
- [Alfred Dependency Bundler Demo (Python)](http://www.packal.org/workflow/alfred-dependency-bundler-demo-python)
  ([GitHub repo](https://github.com/deanishe/alfred-bundler-python-demo))
  by [deanishe](http://www.packal.org/users/deanishe)
  ([on GitHub](https://github.com/deanishe/)).
  Demonstration on how to use the Alfred Bundler in Python.
- [alfred-ime](http://www.packal.org/workflow/ime)
  ([GitHub repo](https://github.com/owenwater/alfred-ime))
  by [owenwater](http://www.packal.org/users/owenwater)
  ([on GitHub](https://github.com/owenwater/)).
  A Input method workflow based on Google Input Tools.
- [AppScripts](http://www.packal.org/workflow/appscripts)
  ([GitHub repo](https://github.com/deanishe/alfred-appscripts))
  by [deanishe](http://www.packal.org/users/deanishe)
  ([on GitHub](https://github.com/deanishe/)).
  List, search and run/open AppleScripts for the active application.
- [Better IMDB search](http://www.packal.org/workflow/better-imdb-search)
  by [frankspin](http://www.packal.org/users/frankspin).
  Search IMDB for movies and see results inside of Alfred.
- [BibQuery](http://www.packal.org/workflow/bibquery)
  ([GitHub repo](https://github.com/smargh/alfred_bibquery))
  by [hackademic](http://www.packal.org/users/hackademic)
  ([on GitHub](https://github.com/smargh/)).
  Search BibDesk from the comfort of your keyboard.
- [Blur](http://www.packal.org/workflow/blur)
  by [Tyler Eich](http://www.packal.org/users/tyler-eich).
  Set Alfred's background blur radius.
- [Calendar](http://www.packal.org/workflow/calendar)
  ([GitHub repo](https://github.com/owenwater/alfred-cal))
  by [owenwater](http://www.packal.org/users/owenwater)
  ([on GitHub](https://github.com/owenwater/)).
  Displays a monthly calendar with Alfred Workflow.
- [Code Case](http://www.packal.org/workflow/code-case)
  by [dfay](http://www.packal.org/users/dfay).
  Case Converter for Code.
- [Continuity Support](http://www.packal.org/workflow/continuity-support)
  by [dmarshall](http://www.packal.org/users/dmarshall).
  Enables calling and messaging via contacts or number input.
- [Convert](http://www.packal.org/workflow/convert)
  ([GitHub repo](https://github.com/deanishe/alfred-convert))
  by [deanishe](http://www.packal.org/users/deanishe)
  ([on GitHub](https://github.com/deanishe/)).
  Convert between different units. No Internet connection required.
- [Date Calculator](http://www.packal.org/workflow/date-calculator)
  ([GitHub repo](https://github.com/MuppetGate/Alfred-Workflows-DateCalculator))
  by [MuppetGate](http://www.packal.org/users/muppetgate)
  ([on GitHub](https://github.com/MuppetGate/)).
  A basic date calculator.
- [Digital Ocean status](http://www.packal.org/workflow/digital-ocean-status)
  ([GitHub repo](https://github.com/fspinillo/alfred-digital-ocean))
  by [frankspin](http://www.packal.org/users/frankspin)
  ([on GitHub](https://github.com/fspinillo/)).
  Control your Digital Ocean droplets.
- [Display Brightness](http://www.packal.org/workflow/display-brightness)
  ([GitHub repo](https://github.com/fniephaus/alfred-brightness))
  by [fniephaus](http://www.packal.org/users/fniephaus)
  ([on GitHub](https://github.com/fniephaus/)).
  Adjust your display's brightness with Alfred.
- [Dropbox Client for Alfred](http://www.packal.org/workflow/dropbox-client-alfred)
  ([GitHub repo](https://github.com/fniephaus/alfred-dropbox/))
  by [fniephaus](http://www.packal.org/users/fniephaus)
  ([on GitHub](https://github.com/fniephaus/)).
  Access multiple Dropbox accounts with Alfred.
- [Duden Search](http://www.packal.org/workflow/duden-search)
  ([GitHub repo](https://github.com/deanishe/alfred-duden))
  by [deanishe](http://www.packal.org/users/deanishe)
  ([on GitHub](https://github.com/deanishe/)).
  Search duden.de German dictionary (with auto-suggest).
- [Fabric for Alfred](http://www.packal.org/workflow/fabric-alfred)
  by [fniephaus](http://www.packal.org/users/fniephaus).
  Quickly execute Fabric tasks.
- [Fakeum](http://www.packal.org/workflow/fakeum)
  ([GitHub repo](https://github.com/deanishe/alfred-fakeum/releases))
  by [deanishe](http://www.packal.org/users/deanishe)
  ([on GitHub](https://github.com/deanishe/)).
  Generate fake test data in Alfred.
- [Forvo](http://www.packal.org/workflow/forvo)
  ([GitHub repo](https://github.com/owenwater/alfred-forvo))
  by [owenwater](http://www.packal.org/users/owenwater)
  ([on GitHub](https://github.com/owenwater/)).
  A pronunciation workflow based on Forvo.com.
- [Fuzzy Folders](http://www.packal.org/workflow/fuzzy-folders)
  ([GitHub repo](https://github.com/deanishe/alfred-fuzzyfolders))
  by [deanishe](http://www.packal.org/users/deanishe)
  ([on GitHub](https://github.com/deanishe/)).
  Fuzzy search across folder subtrees.
- [Git Repos](http://www.packal.org/workflow/git-repos)
  ([GitHub repo](https://github.com/deanishe/alfred-repos))
  by [deanishe](http://www.packal.org/users/deanishe)
  ([on GitHub](https://github.com/deanishe/)).
  Browse, search and open Git repositories from within Alfred.
- [Glosbe Translation](http://www.packal.org/workflow/glosbe-translation)
  by [deanishe](http://www.packal.org/users/deanishe).
  Translate text using Glosbe.com.
- [Gmail Client for Alfred](http://www.packal.org/workflow/gmail-client-alfred)
  ([GitHub repo](https://github.com/fniephaus/alfred-gmail))
  by [fniephaus](http://www.packal.org/users/fniephaus)
  ([on GitHub](https://github.com/fniephaus/)).
  Manage your Gmail inbox with Alfred.
- [HackerNews for Alfred](http://www.packal.org/workflow/hackernews-alfred)
  ([GitHub repo](https://github.com/fniephaus/alfred-hackernews))
  by [fniephaus](http://www.packal.org/users/fniephaus)
  ([on GitHub](https://github.com/fniephaus/)).
  Read Hacker News with Alfred.
- [Homebrew and Cask for Alfred](http://www.packal.org/workflow/homebrew-and-cask-alfred)
  ([GitHub repo](https://github.com/fniephaus/alfred-homebrew))
  by [fniephaus](http://www.packal.org/users/fniephaus)
  ([on GitHub](https://github.com/fniephaus/)).
  Easily control Homebrew and Cask with Alfred.
- [IPython Notebooks](http://www.packal.org/workflow/ipython-notebooks)
  ([GitHub repo](https://github.com/nkeim/alfred-ipython-notebook))
  by [nkeim](http://www.packal.org/users/nkeim)
  ([on GitHub](https://github.com/nkeim/)).
  Search notebook titles on your IPython notebook server.
- [Jenkins](http://www.packal.org/workflow/jenkins)
  ([GitHub repo](https://github.com/Amwam/Jenkins-Alfred-Workflow/))
  by [Amwam](http://www.packal.org/users/amwam)
  ([on GitHub](https://github.com/Amwam/)).
  Show and search through jobs on Jenkins.
- [KA Torrents](http://www.packal.org/workflow/ka-torrents)
  by [hackademic](http://www.packal.org/users/hackademic).
  Search and download torrents from kickass.so.
- [Laser SSH](http://www.packal.org/workflow/laser-ssh)
  by [paperElectron](http://www.packal.org/users/paperelectron).
  Choose SSH connection from filterable list.
- [LastPass Vault Manager](http://www.packal.org/workflow/lastpass-vault-manager)
  ([GitHub repo](https://github.com/bachya/lp-vault-manager))
  by [bachya](http://www.packal.org/users/bachya)
  ([on GitHub](https://github.com/bachya/)).
  A workflow to interact with a LastPass vault.
- [LibGen](http://www.packal.org/workflow/libgen)
  ([GitHub repo](https://github.com/smargh/alfred_libgen))
  by [hackademic](http://www.packal.org/users/hackademic)
  ([on GitHub](https://github.com/smargh/)).
  Search and Download pdfs and ebooks from Library Genesis.
- [Movies](http://www.packal.org/workflow/movies)
  ([GitHub repo](https://github.com/tmcknight/Movies-Alfred-Workflow))
  by [tone](http://www.packal.org/users/tone)
  ([on GitHub](https://github.com/tmcknight/)).
  Search for movies to find ratings from a few sites.
- [Network Location](http://www.packal.org/workflow/network-location)
  ([GitHub repo](https://github.com/deanishe/alfred-network-location))
  by [deanishe](http://www.packal.org/users/deanishe)
  ([on GitHub](https://github.com/deanishe/)).
  List, filter and activate network locations from within Alfred.
- [Packal Workflow Search](http://www.packal.org/workflow/packal-workflow-search)
  ([GitHub repo](https://github.com/deanishe/alfred-packal-search))
  by [deanishe](http://www.packal.org/users/deanishe)
  ([on GitHub](https://github.com/deanishe/)).
  Search Packal.org from the comfort of Alfred.
- [Pandoctor](http://www.packal.org/workflow/pandoctor)
  ([GitHub repo](https://github.com/smargh/alfred_pandoctor))
  by [hackademic](http://www.packal.org/users/hackademic)
  ([on GitHub](https://github.com/smargh/)).
  An Alfred GUI for Pandoc.
- [Parsers](http://www.packal.org/workflow/parsers)
  ([GitHub repo](https://github.com/smargh/alfred_parsers))
  by [hackademic](http://www.packal.org/users/hackademic)
  ([on GitHub](https://github.com/smargh/)).
  Greek and Latin parsers.
- [Percent Change](http://www.packal.org/workflow/percent-change)
  ([GitHub repo](https://github.com/bradmontgomery/alfred-percent-change))
  by [bkmontgomery](http://www.packal.org/users/bkmontgomery)
  ([on GitHub](https://github.com/bradmontgomery/)).
  Easily do percentage calculations.
- [Pocket for Alfred](http://www.packal.org/workflow/pocket-alfred)
  ([GitHub repo](https://github.com/fniephaus/alfred-pocket))
  by [fniephaus](http://www.packal.org/users/fniephaus)
  ([on GitHub](https://github.com/fniephaus/)).
  Manage your Pocket list with Alfred.
- [PWS History](http://www.packal.org/workflow/pws-history)
  ([GitHub repo](https://github.com/hrbrmstr/alfred-pws))
  by [hrbrmstr](http://www.packal.org/users/hrbrmstr)
  ([on GitHub](https://github.com/hrbrmstr/)).
  Retrieve personal weather station history from Weather Underground.
- [Quick Stocks](http://www.packal.org/workflow/quick-stocks)
  by [paperElectron](http://www.packal.org/users/paperelectron).
  Add some stock symbols for Alfred to check for you.
- [Readability for Alfred](http://www.packal.org/workflow/readability-alfred)
  ([GitHub repo](https://github.com/fniephaus/alfred-readability/))
  by [fniephaus](http://www.packal.org/users/fniephaus)
  ([on GitHub](https://github.com/fniephaus/)).
  Manage your Readability list with Alfred.
- [Reddit](http://www.packal.org/workflow/reddit)
  ([GitHub repo](https://github.com/deanishe/alfred-reddit))
  by [deanishe](http://www.packal.org/users/deanishe)
  ([on GitHub](https://github.com/deanishe/)).
  Browse Reddit from Alfred.
- [Relative Dates](http://www.packal.org/workflow/relative-dates)
  ([GitHub repo](https://github.com/deanishe/alfred-relative-dates))
  by [deanishe](http://www.packal.org/users/deanishe)
  ([on GitHub](https://github.com/deanishe/)).
  Generate relative dates based on a simple input format.
- [Resolve URL](http://www.packal.org/workflow/resolve-url)
  ([GitHub repo](https://github.com/deanishe/alfred-resolve-url))
  by [deanishe](http://www.packal.org/users/deanishe)
  ([on GitHub](https://github.com/deanishe/)).
  Follows any HTTP redirects and returns the canonical URL. Also displays information about the primary host (hostname, IP address(es), aliases).
- [Searchio!](http://www.packal.org/workflow/searchio)
  ([GitHub repo](https://github.com/deanishe/alfred-searchio))
  by [deanishe](http://www.packal.org/users/deanishe)
  ([on GitHub](https://github.com/deanishe/)).
  Auto-suggest search results from multiple search engines and languages.
- [SEND](http://www.packal.org/workflow/send)
  by [hackademic](http://www.packal.org/users/hackademic).
  Send documents to the cloud.
- [Skimmer](http://www.packal.org/workflow/skimmer)
  ([GitHub repo](https://github.com/smargh/alfred-Skimmer))
  by [hackademic](http://www.packal.org/users/hackademic)
  ([on GitHub](https://github.com/smargh/)).
  Actions for PDF viewer Skim.
- [slackfred](http://www.packal.org/workflow/slackfred)
  ([GitHub repo](https://github.com/fspinillo/slackfred))
  by [frankspin](http://www.packal.org/users/frankspin)
  ([on GitHub](https://github.com/fspinillo/)).
  Interact with the chat service Slack via Alfred.
- [Snippets](http://www.packal.org/workflow/snippets)
  ([GitHub repo](https://github.com/smargh/alfred_snippets))
  by [hackademic](http://www.packal.org/users/hackademic)
  ([on GitHub](https://github.com/smargh/)).
  Simple, document-specific text snippets.
- [Spritzr](http://www.packal.org/workflow/spritzr)
  ([GitHub repo](https://github.com/smargh/alfred_spritzr))
  by [hackademic](http://www.packal.org/users/hackademic)
  ([on GitHub](https://github.com/smargh/)).
  An Alfred Speed-Reader.
- [StackOverflow Search](http://www.packal.org/workflow/stackoverflow-search)
  ([GitHub repo](https://github.com/deanishe/alfred-stackoverflow))
  by [deanishe](http://www.packal.org/users/deanishe)
  ([on GitHub](https://github.com/deanishe/)).
  Search StackOverflow.com from Alfred.
- [Sublime Text Projects](http://www.packal.org/workflow/sublime-text-projects)
  ([GitHub repo](https://github.com/deanishe/alfred-sublime-text))
  by [deanishe](http://www.packal.org/users/deanishe)
  ([on GitHub](https://github.com/deanishe/)).
  View, filter and open your Sublime Text (2 and 3) project files.
- [Torrent](http://www.packal.org/workflow/torrent)
  ([GitHub repo](https://github.com/bfw/alfred-torrent))
  by [bfw](http://www.packal.org/users/bfw)
  ([on GitHub](https://github.com/bfw/)).
  Search for torrents, choose among the results in Alfred and start the download in uTorrent.
- [Travis CI for Alfred](http://www.packal.org/workflow/travis-ci-alfred)
  by [fniephaus](http://www.packal.org/users/fniephaus).
  Quickly check build statuses on travis-ci.org.
- [UberTime](http://www.packal.org/workflow/ubertime)
  ([GitHub repo](https://github.com/fspinillo/alfred-uber))
  by [frankspin](http://www.packal.org/users/frankspin)
  ([on GitHub](https://github.com/fspinillo/)).
  Check estimated pick up time for Uber based on inputted address.
- [VagrantUP](http://www.packal.org/workflow/vagrantup)
  ([GitHub repo](https://github.com/m1keil/alfred-vagrant-workflow))
  by [m1keil](http://www.packal.org/users/m1keil)
  ([on GitHub](https://github.com/m1keil/)).
  List and control Vagrant environments with Alfred2.
- [VM Control](http://www.packal.org/workflow/vm-control)
  ([GitHub repo](https://github.com/fniephaus/alfred-vmcontrol))
  by [fniephaus](http://www.packal.org/users/fniephaus)
  ([on GitHub](https://github.com/fniephaus/)).
  Control your Parallels and Virtual Box virtual machines.
- [Wikify](http://www.packal.org/workflow/wikify)
  ([GitHub repo](https://github.com/smargh/alfred_EN-Wikify))
  by [hackademic](http://www.packal.org/users/hackademic)
  ([on GitHub](https://github.com/smargh/)).
  Your little Evernote Wiki-Helper.
- [ZotQuery](http://www.packal.org/workflow/zotquery)
  ([GitHub repo](https://github.com/smargh/alfred_zotquery))
  by [hackademic](http://www.packal.org/users/hackademic)
  ([on GitHub](https://github.com/smargh/)).
  Search Zotero. From the Comfort of Your Keyboard.



[alfred]: http://www.alfredapp.com/
[cc]: https://creativecommons.org/licenses/by-nc/4.0/legalcode
[coveralls]: https://coveralls.io/r/deanishe/alfred-workflow?branch=master
[deanishe]: https://github.com/deanishe
[docs-api]: http://www.deanishe.net/alfred-workflow/#api-documentation
[docs-rtd]: https://alfredworkflow.readthedocs.org/
[docs]: http://www.deanishe.net/alfred-workflow/
[fniephaus]: https://github.com/fniephaus
[owenwater]: https://github.com/owenwater
[issues]: https://github.com/deanishe/alfred-workflow/issues
[landscape]: https://landscape.io/github/deanishe/alfred-workflow/master
[packal]: http://www.packal.org/
[pep8]: http://legacy.python.org/dev/peps/pep-0008/
[pulls]: https://github.com/deanishe/alfred-workflow/pulls
[pypi]: https://pypi.python.org/pypi/Alfred-Workflow/
[releases]: https://github.com/deanishe/alfred-workflow/releases
[repo]: https://github.com/deanishe/alfred-workflow
[requests]: http://docs.python-requests.org/en/latest/
[rtd]: https://readthedocs.org/
[shield-coveralls]: https://img.shields.io/coveralls/deanishe/alfred-workflow.svg?style=flat
[shield-docs]: https://readthedocs.org/projects/alfredworkflow/badge/?version=latest&style=flat
[shield-download]: https://pypip.in/download/Alfred-Workflow/badge.svg?style=flat
[shield-health]: https://landscape.io/github/deanishe/alfred-workflow/master/landscape.png?style=flat
[shield-licence]: https://pypip.in/license/Alfred-Workflow/badge.svg?style=flat
[shield-status]: https://pypip.in/status/Alfred-Workflow/badge.svg?style=flat
[shield-travis]: https://img.shields.io/travis/deanishe/alfred-workflow.svg?style=flat
[shield-version]: https://pypip.in/version/Alfred-Workflow/badge.svg?text=version&style=flat
[smargh]: https://github.com/smargh
[sphinx]: http://sphinx-doc.org/
[travis]: https://travis-ci.org/deanishe/alfred-workflow
[cheeseshop]: https://pypi.python.org/pypi
[pip-docs]: https://pip.pypa.io/en/latest/
