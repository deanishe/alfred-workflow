
# Alfred-Workflow #

A helper library in Python for authors of workflows for [Alfred 2](http://www.alfredapp.com/).

## Features ##

- Catches and logs workflow errors for easier development and support
- Auto-saves settings
- Super-simple data caching
- Simple generation of Alfred feedback (XML output)
- Input decoding
- Lightweight web API with [Requests](http://docs.python-requests.org/en/latest/)-like interface
- Pre-configured logging
- Built-in maintenance via workflow/CLI arguments
- Painlessly add directories to `sys.path`

## Installation ##

Download this repository and copy the `workflow` directory contained within it to the root
of your workflow:

	Your Workflow/
		info.plist
		icon.png
		workflow/
			__init__.py
			workflow.py
			web.py
			etc.
		yourscript.py
		etc.

## Usage ##

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

### Settings ###

The `Workflow.settings` attribute is a dictionary that is automatically saved (as a JSON file) when it's changed. You can initialise the settings by passing a dictionary as the `default_settings` argument when you create `Workflow()`:

```python
wf = Workflow(default_settings={'key': 'value'})
```

If the settings file already exists, the defaults will be ignored.

### Data directories and simple data caching ###

Each Alfred workflow is assigned directories tucked away in `~/Library` for temporary (cache) data and permanent data. `Workflow` makes these available as `Workflow.cachedir` and `Workflow.datadir`.

There are also the convenience methods `Workflow.cachefile(filename)` and `Workflow.datafile(filename)` which will return the full path to file `filename` within the respective workflow directory.

Workflows get run frequently by Alfred, so it's often a good idea to cache data that takes time to generate (e.g. listing files on the filesystem or getting data from a web service). To these ends, the method `Workflow.cached_data` is provided. For example:

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

If the function that retrieves data requires arguments, wrap it in an inline function that doesn't:

```python
def get_web_data(query):
    return web.get('http://www.example.com', params={'query': query}).json()

def main(wf):
    query = 'Tom Jones'
    # Create wrapper function that has access to local variables
    def wrapper():
        return get_web_data(query)
    # Save data from `get_web_data` for 30 seconds under
    # the key `example`
    data = wf.cached_data('example', wrapper, max_age=30)
    for datum in data:
        wf.add_item(datum['title'], datum['author'])
    wf.send_feedback()
```

### Web ###

`workflow.web` is a very lightweight module to access web-based resources using a [Requests](http://docs.python-requests.org/en/latest/)-like interface. It is a thin wrapper around Python's built-in web libraries (`urllib`, `urllib2` etc.) to provide a more intuitive interface. Obviously, it provides only a tiny fraction of the functionality of the actual Requests library, but weighs in at ~0.5% of the size.

It supports GET and POST requests, form submissions and file uploads, JSON responses and very basic text decoding (to give you Unicode text).

Please consider using `web.py` instead of bundling Requests with your workflow if it meets your requirements. Requests is some 2.1 MB and a few copies of it bundled with workflows can quickly bloat your workflows directory.

The API aims to ape Requests' as closely as possible:

```python
# Fetch a web page
r = web.get('http://www.example.com/')
# HTTP respose code
r.status_code
# Throw exception if request failed
r.raise_for_status()
# Access exception
r.error
# Unicode content of retrieved resource
r.text
# Parse response as JSON
r.json()

# URL with GET parameters
r = web.get('http://www.example.com/', params={'query': 'find me', 'format': 'json'})
# http://www.example.com/?query=find%20me&format=json
r.url

# POST request sending form data
r = web.post('http://www.example.com/', data={'artist': 'Tom Jones', 'song': "It's not unusual"})

# File upload
files = {'fieldname' : {'filename': "It's not unusual.mp3",
                        'content': open("It's not unusual.mp3", 'rb').read()}
}
r = web.post('http://www.example.com/upload/', files=files)
```

### Unicode and encoding/decoding ###

`workflow` uses Unicode internally and provides the `Workflow.decode` method for decoding byte strings to Unicode. The Alfred/CLI arguments in `Workflow.args` are automatically decoded.

You should also ensure that any data you load from external sources are also decoded to Unicode.

By default `Workflow.decode` normalises Unicode text to the **NFC** form. This is the default for Python and should work well with strings in scripts and from web services. OS X, however, uses **NFD** normalisation, so if you workflow primarily uses data from the system (including the filesystem via `subprocess` or `os.listdir` etc.), you should set the default normalisation to **NFD** by calling `Workflow` with the `normalization='NFD'` argument.

If possible, test your workflow with non-ASCII text to ensure it behaves properly.

### "Magic" arguments ###

`workflow` supports a few special arguments, which it will act upon automatically if they are the first argument passed to your script (via Alfred or the CLI). These all begin with `workflow:` and are:

- `workflow:openlog` : Opens the workflow's log file in the default app (usually Console.app). The log will contain any errors that have occurred including corresponding tracebacks. It will also contain any messages logged with `Workflow.logger`.
- `workflow:delcache` : Delete all cached files. Useful for resetting the workflow.
- `workflow:delsettings` : Delete the settings file. Useful for resetting the workflow.

### Extending sys.path ###

If your workflow has other dependencies, you can install this in a subdirectory and add it to `sys.path` by passing the `libraries=['dir/path/1', 'dir/path/2', ...]` argument to `Workflow()`. This
will only work if you're initialising `Workflow` *before* performing imports.

### Logging ###

The `Workflow` class provides a pre-configured `logging.Logger` instance at `Workflow.logger`. This will log all messages both to the Terminal (if running as a CLI script) and to the workflow's log file, named `workflow.log` and stored in the workflow's cache directory. You can open it by passing `workflow:openlog` as the first argument to your workflow script.
