
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

- AppScripts ([GitHub](https://github.com/deanishe/alfred-appscripts), [Packal](http://www.packal.org/users/deanishe))
- FuzzyFolders ([GitHub](https://github.com/deanishe/alfred-fuzzyfolders), [Packal](http://www.packal.org/workflow/fuzzy-folders))
- ZotQuery ([GitHub](https://github.com/smargh/alfred_zotquery), [Packal](http://www.packal.org/workflow/zotquery))
