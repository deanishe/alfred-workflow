
# Alfred-Workflow #

A helper library in Python for authors of workflows for [Alfred 2](http://www.alfredapp.com/).

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

## Installation ##

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
        workflow-1.3.zip
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


## Contributors ##

- [Dean Jackson](https://github.com/deanishe)
- [Stephen Margheim](https://github.com/smargh)

## Workflows using Alfred-Workflow ##

These are some of the Alfred workflows that use this library.

- [Alfred Backblaze](http://www.packal.org/workflow/alfred-backblaze) by XedMada. Pause and Start Backblaze online backups.
- [AppScripts](http://www.packal.org/workflow/appscripts) by deanishe. List, search and run/open AppleScripts for the active application.
- [BibQuery](http://www.packal.org/workflow/bibquery) by hackademic. Search BibDesk from the comfort of your keyboard.
- [Blur](http://www.packal.org/workflow/blur) by Tyler Eich. Set Alfred's background blur radius.
- [Convert](http://www.packal.org/workflow/convert) by deanishe. Convert between different units. No Internet connection required.
- [Date Calculator](http://www.packal.org/workflow/date-calculator) by MuppetGate. A very basic date calculator.
- [Dropbox Client for Alfred](http://www.packal.org/workflow/dropbox-client-alfred) by fniephaus. Access multiple Dropbox accounts with Alfred.
- [Fabric for Alfred](http://www.packal.org/workflow/fabric-alfred) by fniephaus. Quickly execute Fabric tasks.
- [Fuzzy Folders](http://www.packal.org/workflow/fuzzy-folders) by deanishe. Fuzzy search across folder subtrees.
- [Glosbe Translation](http://www.packal.org/workflow/glosbe-translation) by deanishe. Translate text using Glosbe.com.
- [IPython Notebooks](http://www.packal.org/workflow/ipython-notebooks) by nkeim. Search notebook titles on your IPython notebook server.
- [Network Location](http://www.packal.org/workflow/network-location) by deanishe. List, filter and activate network locations from within Alfred.
- [Packal Workflow Search](http://www.packal.org/workflow/packal-workflow-search) by deanishe. Search Packal.org from the comfort of Alfred.
- [Parsers](http://www.packal.org/workflow/parsers) by hackademic. Greek and Latin parsers.
- [Pocket for Alfred](http://www.packal.org/workflow/pocket-alfred) by fniephaus. Manage your Pocket list with Alfred.
- [Readability for Alfred](http://www.packal.org/workflow/readability-alfred) by fniephaus. Manage your Readability list with Alfred.
- [Relative Dates](http://www.packal.org/workflow/relative-dates) by deanishe. Generate relative dates based on a simple input format.
- [SEND](http://www.packal.org/workflow/send) by hackademic. Send documents to the cloud.
- [Skimmer](http://www.packal.org/workflow/skimmer) by hackademic. Actions for PDF viewer Skim.
- [Spritzr](http://www.packal.org/workflow/spritzr) by hackademic. An Alfred Speed-Reader.
- [Sublime Text Projects](http://www.packal.org/workflow/sublime-text-projects) by deanishe. View, filter and open your Sublime Text (2 and 3) project files.
- [Travis CI for Alfred](http://www.packal.org/workflow/travis-ci-alfred) by fniephaus. Quickly check build statuses on travis-ci.org.
- [VM Control](http://www.packal.org/workflow/vm-control) by fniephaus. Control your Parallels and Virtual Box virtual machines.
- [Wikify](http://www.packal.org/workflow/wikify) by hackademic. Your little Evernote Wiki-Helper.
- [ZotQuery](http://www.packal.org/workflow/zotquery) by hackademic. Search Zotero. From the Comfort of Your Keyboard.