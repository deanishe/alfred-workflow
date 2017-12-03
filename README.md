
<img src="./icon.png" width="200" height="200">

Alfred-Workflow
===============

A helper library in Python for authors of workflows for [Alfred 2 and 3][alfred].

[![Build Status][shield-travis]][travis] [![Coverage Status][shield-coveralls]][coveralls] [![Latest Version][shield-version]][pypi] [![Development Status][shield-status]][pypi] [![Supported Python Versions][shield-pyversions]][pypi]

<!-- [![Downloads][shield-download]][pypi] -->

Supports OS X 10.6+ and Python 2.6 and 2.7 (Alfred 3 is 10.9+/2.7 only).

Alfred-Workflow takes the grunt work out of writing a workflow by giving you the tools to create a fast and featureful Alfred workflow from an API, application or library in minutes.

The only library, in any language, that *always* supports all current Alfred features.

Features
--------

- Auto-saved settings API for your workflow
- Super-simple data caching
- Fuzzy filtering (with smart diacritic folding)
- Keychain support for secure storage of passwords, API keys etc.
- Simple generation of Alfred feedback (JSON/XML output)
- Input/output decoding for handling non-ASCII text
- Lightweight web API with [Requests][requests]-like interface
- Catches and logs workflow errors for easier development and support
- "Magic" arguments to help development/debugging
- Pre-configured logging
- Easily launch background tasks (daemons) to keep your workflow responsive
- Automatically check for workflow updates via GitHub releases
- Post notifications via Notification Center
- Painlessly add directories to `sys.path`


### Alfred 3-only features ###

- Set workflow variables from code
- Advanced modifiers
- Alfred 3-only updates (won't break Alfred 2 installs)
- Re-running of Script Filters


Contents
--------

- [Installation](#installation)
    - [With pip](#with-pip)
    - [From source](#from-source)
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


Installation
------------

**Note**: If you intend to distribute your workflow to other users, you should include Alfred-Workflow (and other Python libraries your workflow requires) within your workflow's directory as described below. **Do not** ask users to install anything into their system Python. Python installations cannot support multiple versions of the same library, so if you rely on globally-installed libraries, the chances are very good that your workflow will sooner or later break—or be broken by—some other software doing the same naughty thing.


### With pip ###

You can install Alfred-Workflow directly into your workflow with:

```bash
# from your workflow directory
pip install --target=. Alfred-Workflow
```

You can install any other library available on the [Cheese Shop][cheeseshop] the same way. See the [pip documentation][pip-docs] for more information.

It is highly advisable to bundle all your workflow's dependencies with your workflow in this way. That way, it will "just work".


### From source ###

1. Download the `alfred-workflow-X.X.X.zip` from the [GitHub releases page][releases].
2. Extract the ZIP archive and place the `workflow` directory in the root folder of your workflow (where `info.plist` is).

Your workflow should look something like this:

    Your Workflow/
        info.plist
        icon.png
        workflow/
            __init__.py
            background.py
            notify.py
            Notify.tgz
            update.py
            version
            web.py
            workflow.py
        yourscript.py
        etc.

Alternatively, you can clone/download the Alfred-Workflow [repository][repo] and copy the `workflow` subdirectory to your workflow's root directory.


Usage
-----

A few examples of how to use Alfred-Workflow.


### Workflow script skeleton ###

Set up your workflow scripts as follows (if you wish to use the built-in error handling or `sys.path` modification):

```python
#!/usr/bin/python
# encoding: utf-8

import sys

from workflow import Workflow


def main(wf):
    # The Workflow instance will be passed to the function
    # you call from `Workflow.run`. Not so useful, as
    # the `wf` object created in `if __name__ ...` below is global.
    #
    # Your imports go here if you want to catch import errors (not a bad idea)
    # or if the modules/packages are in a directory added via `Workflow(libraries=...)`
    import somemodule
    import anothermodule
    # Get args from Workflow, already in normalized Unicode
    args = wf.args

    # Do stuff here ...

    # Add an item to Alfred feedback
    wf.add_item(u'Item title', u'Item subtitle')

    # Send output to Alfred. You can only call this once.
    # Well, you *can* call it multiple times, but Alfred won't be listening
    # any more...
    wf.send_feedback()


if __name__ == '__main__':
    # Create a global `Workflow` object
    wf = Workflow()
    # Call your entry function via `Workflow.run()` to enable its helper
    # functions, like exception catching, ARGV normalization, magic
    # arguments etc.
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
r = web.post('http://www.example.com/',
             data={'artist': 'Tom Jones', 'song': "It's not unusual"})
```

Upload a file:

```python
files = {'fieldname' : {'filename': "It's not unusual.mp3",
                        'content': open("It's not unusual.mp3", 'rb').read()}
}
r = web.post('http://www.example.com/upload/', files=files)
```

**WARNING**: As this module is based on Python 2's standard HTTP libraries, *on older versions of OS X/Python, it does not validate SSL certificates when making HTTPS connections*. If your workflow uses sensitive passwords/API keys, you should *strongly consider* using the [requests][requests] library upon which the `web.py` API is based.


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


Documentation
-------------

The full documentation, including API docs and a tutorial, can be found at [deanishe.net][docs].

The documentation is also available as a [Dash docset][dash].


Licensing, thanks
-----------------

The code and the documentation are released under the MIT and [Creative Commons Attribution-NonCommercial][cc] licences respectively. See [LICENCE.txt](LICENCE.txt) for details.

The documentation was generated using [Sphinx][sphinx] and a modified version of the [Alabaster][alabaster] theme by [bitprophet][bitprophet].

Many of the cooler ideas in Alfred-Workflow were inspired by [Alfred2-Ruby-Template][ruby-template] by Zhaocai.

The Keychain parser was based on [Python-Keyring][python-keyring] by Jason R. Coombs.


Contributing
------------


### Adding a workflow to the list ###

If you want to add a workflow to the [list of workflows using Alfred-Workflow](#workflows-using-alfred-workflow), **don't add it to this README!** The list is machine-generated from [Packal.org][packal] and the [`library_workflows.tsv`](extras/library_workflows.tsv) file. If your workflow is available on [Packal][packal], it will be added automatically. If not, please add it to [`library_workflows.tsv`](extras/library_workflows.tsv), instead of `README.md`, and submit a corresponding pull request.

The list is not auto-updated, so if you've released a workflow and are keen to see it in this list, please [open an issue][issues] asking me to update the list.


### Bug reports, pull requests ###

Bug reports, feature suggestions and pull requests are very welcome. Head over to the [issues][issues] if you have a feature request or a bug report.

**Please note:** that the only supported versions of Python are the Apple
system Pythons installed on OS X 10.6+ (i.e. `/usr/bin/python`). Any pull
requests that break compatibility with these Pythons will be rejected out of
hand.

Compatibility with other Pythons is a low priority. Pull requests adding
compatibility with other Pythons will be rejected if they add significant
complexity or additional dependencies, such as `six`.

If you want to make a pull request, do that [here][pulls], but please bear the following in mind:

- Please open pull requests against the `develop` branch. I try to keep `master` in sync with the latest release (at least regarding any files included in releases). `master` and `develop` are *usually* in sync, but if I'm working on new features, they'll be in `develop` and won't be pushed to `master` until they're ready for release.
- Alfred-Workflow has very close to 100% test coverage. "Proof-of-concept" pull requests without tests are more than welcome. However, please be prepared to add the appropriate tests if you want your pull request to be ultimately accepted.
- Complete coverage is *only a proxy* for decent tests. Tests should also cover a decent variety of valid/invalid input. For example, if the code *could potentially* be handed non-ASCII input, it should be tested with non-ASCII input.
- Code should be [PEP8][pep8]-compliant as far as is reasonable. Any decent code editor has a PEP8 plugin that will warn you of potential transgressions.
- Please choose your function, method and argument names carefully, with an eye to the existing names. Obviousness is more important than brevity.
- Document your code using the [Sphinx ReST format][sphinx]. Even if your function/method isn't user-facing, some other developer will be looking at it. Even if it's only a one-liner, the developer may be looking at [the docs][docs-api] in a browser, not at the source code.
  If you don't feel comfortable writing English, I'd be happy to write the docs for you, but please ensure the code is easily understandable (i.e. comment the code if it's not totally obvious).
- Performance counts. By default, Alfred will try to run a workflow anew on every keypress. As a rule, 0.3 seconds execution time is decent, 0.2 seconds or less is smooth. Alfred-Workflow should do its utmost to consume as little of that time as possible.

The main entry point for unit testing is the `run-tests.sh` script in the root directory. This will fail *if code coverage is < 100%*. Travis-CI also uses this script. Add `# pragma: no cover` with care.


### Contributors ###

- [Dean Jackson][deanishe]
- [Stephen Margheim][smargh]
- [Fabio Niephaus][fniephaus]
- [Owen Min][owenwater]


Tests
-----

Alfred-Workflow includes a full suite of unit tests. Please use the `run-tests.sh` script in the root directory of the repo to run the unit tests: it creates the necessary test environment to run the unit tests. `test_workflow.py` *will* fail if not run via `run-scripts.sh`, but the test suites for the other modules may also be run directly.

Moreover, `run-tests.sh` checks the coverage of the unit tests and will fail if it is below 100%.


Workflows using Alfred-Workflow
-------------------------------

These are some of the Alfred workflows that use this library.

- [10.000ft Scripts](http://www.packal.org/workflow/10000ft-scripts) ([GitHub repo](https://github.com/jceelen/alfred-10000ft-scripts)) by [jceelen](http://www.packal.org/users/jceelen) ([on GitHub](https://github.com/jceelen/)).
  The aim is to make working with 10.000ft faster.
- [17Track](http://www.packal.org/workflow/17track) by [emamuna](http://www.packal.org/users/emamuna).
  Workflow used to track your shipments on 17Track.net.
- [Airmail-to-Todoist](http://www.packal.org/workflow/airmail-todoist) ([GitHub repo](https://github.com/markgrovs/alfred-airmail-to-todoist)) by [mgroves](http://www.packal.org/users/mgroves) ([on GitHub](https://github.com/markgrovs/)).
  Simple way to create a task in Todoist based on a mail in Airmail 3.
- [Airports](http://www.packal.org/workflow/airports) ([GitHub repo](https://github.com/darkwinternight/alfred-airports-workflow/)) by [darkwinternight](http://www.packal.org/users/darkwinternight) ([on GitHub](https://github.com/darkwinternight/)).
  Get information about all airports in the world.
- [Alfred Backblaze](http://www.packal.org/workflow/alfred-backblaze) ([GitHub repo](https://github.com/XedMada/alfred-backblaze)) by [XedMada](http://www.packal.org/users/xedmada) ([on GitHub](https://github.com/XedMada/)).
  Pause and Start Backblaze online backups.
- [Alfred Dependency Bundler Demo (Python)](http://www.packal.org/workflow/alfred-dependency-bundler-demo-python) ([GitHub repo](https://github.com/deanishe/alfred-bundler-python-demo)) by [deanishe](http://www.packal.org/users/deanishe) ([on GitHub](https://github.com/deanishe/)).
  Demonstration on how to use the Alfred Bundler in Python.
- [Alfred Keyword Help](http://www.packal.org/workflow/alfred-keyword-help) ([GitHub repo](https://github.com/pochemuto/alfred-help-workflow)) by [pochemuto](http://www.packal.org/users/pochemuto) ([on GitHub](https://github.com/pochemuto/)).
  Show and filter available keywords.
- [Alfred Soundboard](http://www.packal.org/workflow/alfred-soundboard) by [Steffen](http://www.packal.org/users/steffen).
  A soundboard for alfred at your fingertips.
- [Alfred-Drive-Workflow](http://www.packal.org/workflow/alfred-drive-workflow) ([GitHub repo](https://github.com/azai91/alfred-drive-workflow)) by [azai91](http://www.packal.org/users/azai91) ([on GitHub](https://github.com/azai91/)).
  Browse, search and open Google Drive files from within Alfred.
- [Alfred-HipChat](http://www.packal.org/workflow/alfred-hipchat) ([GitHub repo](https://github.com/zsprackett/alfred-hipchat)) by [zsprackett](http://www.packal.org/users/zsprackett) ([on GitHub](https://github.com/zsprackett/)).
  Allows you to navigate HipChat rooms and IM's from within Alfred.
- [Alfred-Venmo-Workflow](http://www.packal.org/workflow/alfred-venmo-workflow) ([GitHub repo](https://github.com/azai91/alfred-venmo-workflow)) by [azai91](http://www.packal.org/users/azai91) ([on GitHub](https://github.com/azai91/)).
  Pay and charge friends easily in venmo.
- [alfredwl](http://www.packal.org/workflow/alfredwl) ([GitHub repo](https://github.com/nicke5012/alfredwl)) by [nicke5012](http://www.packal.org/users/nicke5012) ([on GitHub](https://github.com/nicke5012/)).
  Wunderlist integration for Alfred2. Allows you to add tasks, show your lists, and show incomplete tasks through Alfred.
- [Alphy](http://www.packal.org/workflow/alphy) ([GitHub repo](https://github.com/maximepeschard/alphy)) by [maximepeschard](http://www.packal.org/users/maximepeschard) ([on GitHub](https://github.com/maximepeschard/)).
  Search and get links for GIFs on Giphy with Alfred.
- [AppScripts](http://www.packal.org/workflow/appscripts) ([GitHub repo](https://github.com/deanishe/alfred-appscripts)) by [deanishe](http://www.packal.org/users/deanishe) ([on GitHub](https://github.com/deanishe/)).
  List, search and run/open AppleScripts for the active application.
- [Ariafred](http://www.packal.org/workflow/ariafred) ([GitHub repo](https://github.com/Wildog/Ariafred)) by [Wildog](http://www.packal.org/users/wildog) ([on GitHub](https://github.com/Wildog/)).
  Manage Aria2 downloads directly in Alfred, with background notification.
- [Atmos](http://www.packal.org/workflow/atmos) ([GitHub repo](https://github.com/therockmandolinist/alfred-atmos)) by [therockmandolinist](http://www.packal.org/users/therockmandolinist) ([on GitHub](https://github.com/therockmandolinist/)).
  An Alfred workflow to find temperature, speed of sound, pressure, and density at queried altitude, according on International Standard Atmosphere model.
- [aws-alfred-workflow](http://www.packal.org/workflow/aws-alfred-workflow) ([GitHub repo](https://github.com/twang817/aws-alfred-workflow)) by [twang](http://www.packal.org/users/twang) ([on GitHub](https://github.com/twang817/)).
  Workflow for searching AWS.
- [Base Converter](http://www.packal.org/workflow/base-converter) ([GitHub repo](https://github.com/ahalbert/alfred-baseconverter)) by [ahalbert](http://www.packal.org/users/ahalbert) ([on GitHub](https://github.com/ahalbert/)).
  Convert arbitrary bases(up to base 32) in Alfred 2 and copy them to the clipboard.
- [Bear](http://www.packal.org/workflow/bear) ([GitHub repo](https://github.com/chrisbro/alfred-bear)) by [chrisbro](http://www.packal.org/users/chrisbro) ([on GitHub](https://github.com/chrisbro/)).
  Search and create Bear notes from Alfred.
- [BeautifulRatio](http://www.packal.org/workflow/beautifulratio) ([GitHub repo](https://github.com/yusuga/alfred-beautifulratio-workflow)) by [yusuga](http://www.packal.org/users/yusuga) ([on GitHub](https://github.com/yusuga/)).
  This workflow calculates the Golden ratio and Silver ratio.
- [Better IMDB search](http://www.packal.org/workflow/better-imdb-search) by [frankspin](http://www.packal.org/users/frankspin).
  Search IMDB for movies and see results inside of Alfred.
- [BibQuery](http://www.packal.org/workflow/bibquery) ([GitHub repo](https://github.com/smargh/alfred_bibquery)) by [hackademic](http://www.packal.org/users/hackademic) ([on GitHub](https://github.com/smargh/)).
  Search BibDesk from the comfort of your keyboard.
- [Bitcoin Exchange Rates](http://www.packal.org/workflow/bitcoin-exchange-rates) ([GitHub repo](https://github.com/BennySamir/Alfred-Workflows)) by [Benny](http://www.packal.org/users/benny) ([on GitHub](https://github.com/BennySamir/)).
  Request current bitcoin exchange rate from blockchain.info.
- [Blur](http://www.packal.org/workflow/blur) by [Tyler Eich](http://www.packal.org/users/tyler-eich).
  Set Alfred's background blur radius.
- [Calendar](http://www.packal.org/workflow/calendar) ([GitHub repo](https://github.com/owenwater/alfred-cal)) by [owenwater](http://www.packal.org/users/owenwater) ([on GitHub](https://github.com/owenwater/)).
  Displays a monthly calendar with Alfred Workflow.
- [Calibre Search](http://www.packal.org/workflow/calibre-search-0) by [gzr2017](http://www.packal.org/users/gzr2017).
  search your e-books in Calibre by name.
- [Call or SMS contact](http://www.packal.org/workflow/call-or-sms-contact) ([GitHub repo](https://github.com/amoose136/call_or_sms_contact)) by [amoose136](http://www.packal.org/users/amoose136) ([on GitHub](https://github.com/amoose136/)).
  Searches through contacts and calls or texts them depending on input. .
- [Capital Weather Gang](http://www.packal.org/workflow/capital-weather-gang) by [jeffsui](http://www.packal.org/users/jeffsui).
  Pulls the Capital Weather Gang RSS Feed.
- [CDN](http://www.packal.org/workflow/alfred-cdn-workflow) ([GitHub repo](https://github.com/azai91/alfred-cdn-workflow)) by [azai91](http://www.packal.org/users/azai91) ([on GitHub](https://github.com/azai91/)).
  Find CDNs quick with Alfred.
- [Cheatsheet](http://www.packal.org/workflow/cheatsheet) ([GitHub repo](https://github.com/mutdmour/alfred-workflow-cheatsheet)) by [mutasem](http://www.packal.org/users/mutasem) ([on GitHub](https://github.com/mutdmour/)).
  Get shortcuts for your tools.
- [Code Case](http://www.packal.org/workflow/code-case) by [dfay](http://www.packal.org/users/dfay).
  Case Converter for Code.
- [Codebox](http://www.packal.org/workflow/codebox) ([GitHub repo](https://github.com/danielecook/codebox-alfred)) by [danielecook](http://www.packal.org/users/danielecook) ([on GitHub](https://github.com/danielecook/)).
  Search codebox snippets.
- [Continuity Support](http://www.packal.org/workflow/continuity-support) by [dmarshall](http://www.packal.org/users/dmarshall).
  Enables calling and messaging via contacts or number input.
- [Convert](http://www.packal.org/workflow/convert) ([GitHub repo](https://github.com/deanishe/alfred-convert)) by [deanishe](http://www.packal.org/users/deanishe) ([on GitHub](https://github.com/deanishe/)).
  Convert between different units. No Internet connection required.
- [Cryptocurrency Exchange](http://www.packal.org/workflow/cryptocurrency-exchange) ([GitHub repo](https://github.com/Zhangxi-Lam/alfred-cryptocurrency)) by [JaycezxL1n](http://www.packal.org/users/jaycezxl1n) ([on GitHub](https://github.com/Zhangxi-Lam/)).
  Show the information of various of virtual currency, convert between cryptocurrencies.
- [CryptoCurrency Price Tracker](http://www.packal.org/workflow/cryptocurrency-price-tracker) ([GitHub repo](https://github.com/rhlsthrm/alfred-crypto-tracker/tree/master)) by [rhlsthrm](http://www.packal.org/users/rhlsthrm) ([on GitHub](https://github.com/rhlsthrm/)).
  Quickly check cryptocurrency prices.
- [Currency Exchange](http://www.packal.org/workflow/currency-exchange) ([GitHub repo](https://github.com/daninfpj/currency-exchange)) by [daninfpj](http://www.packal.org/users/daninfpj) ([on GitHub](https://github.com/daninfpj/)).
  Alfred workflow to convert between currencies (including Bitcoin).
- [Date Calculator](http://www.packal.org/workflow/date-calculator) ([GitHub repo](https://github.com/MuppetGate/Alfred-Workflows-DateCalculator)) by [MuppetGate](http://www.packal.org/users/muppetgate) ([on GitHub](https://github.com/MuppetGate/)).
  A basic date calculator.
- [DeepL translation](http://www.packal.org/workflow/deepl-translation) ([GitHub repo](https://github.com/Skoda091/alfred-deepl)) by [Skoda091](http://www.packal.org/users/skoda091) ([on GitHub](https://github.com/Skoda091/)).
  This Alfred workflow uses DeepL API for translations.
- [Default Folder X](http://www.packal.org/workflow/default-folder-x) ([GitHub repo](https://github.com/deanishe/alfred-default-folder-x)) by [deanishe](http://www.packal.org/users/deanishe) ([on GitHub](https://github.com/deanishe/)).
  Show and search Default Folder X favourites and recent items.
- [Dict.cc for Alfred](http://www.packal.org/workflow/dictcc-alfred) ([GitHub repo](https://github.com/Kavakuo/Dict.cc-Alfred-Workflow)) by [PhilippN](http://www.packal.org/users/philippn) ([on GitHub](https://github.com/Kavakuo/)).
  This Alfred workflow uses the offline translation databases provided by dict.cc.
- [Digital Ocean status](http://www.packal.org/workflow/digital-ocean-status) ([GitHub repo](https://github.com/fspinillo/alfred-digital-ocean)) by [frankspin](http://www.packal.org/users/frankspin) ([on GitHub](https://github.com/fspinillo/)).
  Control your Digital Ocean droplets.
- [Display Brightness](http://www.packal.org/workflow/display-brightness) ([GitHub repo](https://github.com/fniephaus/alfred-brightness)) by [fniephaus](http://www.packal.org/users/fniephaus) ([on GitHub](https://github.com/fniephaus/)).
  Adjust your display's brightness with Alfred.
- [Docker Cloud](http://www.packal.org/workflow/docker-cloud) by [amigold](http://www.packal.org/users/amigold).
  Shortcuts to quickly navigate Docker Cloud services and node clusters.
- [Dropbox Client for Alfred](http://www.packal.org/workflow/dropbox-client-alfred) ([GitHub repo](https://github.com/fniephaus/alfred-dropbox/)) by [fniephaus](http://www.packal.org/users/fniephaus) ([on GitHub](https://github.com/fniephaus/)).
  Access multiple Dropbox accounts with Alfred.
- [Duden Search](http://www.packal.org/workflow/duden-search) ([GitHub repo](https://github.com/deanishe/alfred-duden)) by [deanishe](http://www.packal.org/users/deanishe) ([on GitHub](https://github.com/deanishe/)).
  Search duden.de German dictionary (with auto-suggest).
- [Ekşi Sözlük Search](http://www.packal.org/workflow/eksi-sozluk-search) ([GitHub repo](https://github.com/ttuygun/alfred-eksi-sozluk-workflow)) by [ttuygun](http://www.packal.org/users/ttuygun) ([on GitHub](https://github.com/ttuygun/)).
  Search Turkey's eksisozluk.com.
- [Emoji Taco](http://www.packal.org/workflow/emoji-taco) ([GitHub repo](https://github.com/jeeftor/EmojiTaco/)) by [jeffsui](http://www.packal.org/users/jeffsui) ([on GitHub](https://github.com/jeeftor/)).
  Always up to date - Unicode Emoji workflow includes Taco!.
- [EthexIndia INR Rate](http://www.packal.org/workflow/ethexindia-inr-rate) by [firesofmay](http://www.packal.org/users/firesofmay).
  Current INR Rate for Ether via Ethexindia.
- [Fabric for Alfred](http://www.packal.org/workflow/fabric-alfred) by [fniephaus](http://www.packal.org/users/fniephaus).
  Quickly execute Fabric tasks.
- [Fakeum](http://www.packal.org/workflow/fakeum) ([GitHub repo](https://github.com/deanishe/alfred-fakeum/releases)) by [deanishe](http://www.packal.org/users/deanishe) ([on GitHub](https://github.com/deanishe/)).
  Generate fake test data in Alfred.
- [Forvo](http://www.packal.org/workflow/forvo) ([GitHub repo](https://github.com/owenwater/alfred-forvo)) by [owenwater](http://www.packal.org/users/owenwater) ([on GitHub](https://github.com/owenwater/)).
  A pronunciation workflow based on Forvo.com.
- [Foursquare Search](http://www.packal.org/workflow/foursquare-search) ([GitHub repo](https://github.com/xilopaint/alfred-foursquare)) by [xilopaint](http://www.packal.org/users/xilopaint) ([on GitHub](https://github.com/xilopaint/)).
  Search Foursquare from Alfred 3.
- [Fuzzy Folders](http://www.packal.org/workflow/fuzzy-folders) ([GitHub repo](https://github.com/deanishe/alfred-fuzzyfolders)) by [deanishe](http://www.packal.org/users/deanishe) ([on GitHub](https://github.com/deanishe/)).
  Fuzzy search across folder subtrees.
- [Gank Alfred Workflow](http://www.packal.org/workflow/gank-alfred-workflow) ([GitHub repo](https://github.com/hujiaweibujidao/Gank-Alfred-Workflow)) by [hujiawei](http://www.packal.org/users/hujiawei) ([on GitHub](https://github.com/hujiaweibujidao/)).
  The missing Alfred Workflow for searching ganks(干货) in gank.io.
- [Genymotion](http://www.packal.org/workflow/genymotion) ([GitHub repo](https://github.com/mrz1277/alfred-workflows/tree/master/net.yakiyama.alfred.genymotion)) by [yakiyama](http://www.packal.org/users/yakiyama) ([on GitHub](https://github.com/mrz1277/)).
  Start emulator instantly.
- [Gist](http://www.packal.org/workflow/gist) ([GitHub repo](https://github.com/danielecook/gist-alfred)) by [danielecook](http://www.packal.org/users/danielecook) ([on GitHub](https://github.com/danielecook/)).
  An alfred workflow for accessing github gists as snippets. Supports tags, stars, and private gists.
- [Git Repos](http://www.packal.org/workflow/git-repos) ([GitHub repo](https://github.com/deanishe/alfred-repos)) by [deanishe](http://www.packal.org/users/deanishe) ([on GitHub](https://github.com/deanishe/)).
  Browse, search and open Git repositories from within Alfred.
- [gitignore](http://www.packal.org/workflow/gitignore-0) ([GitHub repo](https://github.com/jdno/alfred2-gitignore)) by [jdno](http://www.packal.org/users/jdno) ([on GitHub](https://github.com/jdno/)).
  Create .gitignore files using Alfred.
- [GitLab](http://www.packal.org/workflow/gitlab) ([GitHub repo](https://github.com/lukewaite/alfred-gitlab)) by [lwaite](http://www.packal.org/users/lwaite) ([on GitHub](https://github.com/lukewaite/)).
  GitLab Project search for Alfred.
- [Glosbe Translation](http://www.packal.org/workflow/glosbe-translation) ([GitHub repo](https://github.com/deanishe/alfred-glosbe)) by [deanishe](http://www.packal.org/users/deanishe) ([on GitHub](https://github.com/deanishe/)).
  Translate text using Glosbe.com.
- [Gmail Client for Alfred](http://www.packal.org/workflow/gmail-client-alfred) ([GitHub repo](https://github.com/fniephaus/alfred-gmail)) by [fniephaus](http://www.packal.org/users/fniephaus) ([on GitHub](https://github.com/fniephaus/)).
  Manage your Gmail inbox with Alfred.
- [Goo Japanese Translater](http://www.packal.org/workflow/goo-japanese-translater) ([GitHub repo](https://github.com/rorvte/alfred-goodict)) by [rorvte](http://www.packal.org/users/rorvte) ([on GitHub](https://github.com/rorvte/)).
  A workflow for searching the definitive Japanese dictionary at http://dictionary.goo.ne.jp.
- [GoToMeeting Tools](http://www.packal.org/workflow/gotomeeting-tools) ([GitHub repo](https://github.com/plongitudes/GoToMeetingTools)) by [tony_et](http://www.packal.org/users/tony_et) ([on GitHub](https://github.com/plongitudes/)).
  GoToMeeting phonebook and launcher.
- [GPG](http://www.packal.org/workflow/gpg) ([GitHub repo](https://github.com/BennySamir/Alfred-Workflows)) by [Benny](http://www.packal.org/users/benny) ([on GitHub](https://github.com/BennySamir/)).
  Sign and encrypt files with GPG.
- [HackerNews for Alfred](http://www.packal.org/workflow/hackernews-alfred) ([GitHub repo](https://github.com/fniephaus/alfred-hackernews)) by [fniephaus](http://www.packal.org/users/fniephaus) ([on GitHub](https://github.com/fniephaus/)).
  Read Hacker News with Alfred.
- [Hayaku](http://www.packal.org/workflow/hayaku) ([GitHub repo](https://github.com/hayaku/hayaku.alfredworkflow)) by [kizu](http://www.packal.org/users/kizu) ([on GitHub](https://github.com/hayaku/)).
  Expands fuzzy CSS abbreviations.
- [HGNC Search](http://www.packal.org/workflow/hgnc-search) ([GitHub repo](https://github.com/danielecook/HGNC-Search)) by [danielecook](http://www.packal.org/users/danielecook) ([on GitHub](https://github.com/danielecook/)).
  Search for human genes.
- [Homebrew and Cask for Alfred](http://www.packal.org/workflow/homebrew-and-cask-alfred) ([GitHub repo](https://github.com/fniephaus/alfred-homebrew)) by [fniephaus](http://www.packal.org/users/fniephaus) ([on GitHub](https://github.com/fniephaus/)).
  Easily control Homebrew and Cask with Alfred.
- [İETT Next Departures](http://www.packal.org/workflow/iett-next-departures) ([GitHub repo](https://github.com/ttuygun/alfred-iett-workflow)) by [ttuygun](http://www.packal.org/users/ttuygun) ([on GitHub](https://github.com/ttuygun/)).
  This alfred workflow shows next departures from beautiful Istanbul's bus service İETT. It uses data from İETT's website.
- [IME](http://www.packal.org/workflow/ime) ([GitHub repo](https://github.com/owenwater/alfred-ime)) by [owenwater](http://www.packal.org/users/owenwater) ([on GitHub](https://github.com/owenwater/)).
  A Input method workflow based on Google Input Tools.
- [iOS Simulator](http://www.packal.org/workflow/ios-simulator) ([GitHub repo](https://github.com/jfro/ios-simulator-apps-alfred-workflow)) by [jfro](http://www.packal.org/users/jfro) ([on GitHub](https://github.com/jfro/)).
  Workflow for finding simulator app data folders, erasing apps and more.
- [IPython Notebooks](http://www.packal.org/workflow/ipython-notebooks) ([GitHub repo](https://github.com/nkeim/alfred-ipython-notebook)) by [nkeim](http://www.packal.org/users/nkeim) ([on GitHub](https://github.com/nkeim/)).
  Search notebook titles on your IPython notebook server.
- [ironmq](http://www.packal.org/workflow/ironmq) by [eldardamari](http://www.packal.org/users/eldardamari).
  Quick productive access to your ironMQ queues .
- [Jenkins](http://www.packal.org/workflow/jenkins) ([GitHub repo](https://github.com/Amwam/Jenkins-Alfred-Workflow/)) by [Amwam](http://www.packal.org/users/amwam) ([on GitHub](https://github.com/Amwam/)).
  Show and search through jobs on Jenkins.
- [Jira Task Manager](http://www.packal.org/workflow/jira-task-manager) ([GitHub repo](https://github.com/miguelpuyol/Jira-Alfred-Workflow)) by [miguelpuyol](http://www.packal.org/users/miguelpuyol) ([on GitHub](https://github.com/miguelpuyol/)).
  A Jira Task Manager for Alfred.
- [Jisho v1.0](http://www.packal.org/workflow/jisho-v10) ([GitHub repo](http://github.com/kylesezhi/alfred-jisho)) by [kylesezhi](http://www.packal.org/users/kylesezhi) ([on GitHub](https://github.com/kylesezhi/)).
  Translate English and Japanese words with Jisho.org.
- [Jisho: Japanese-English Dictionary](http://www.packal.org/workflow/jisho-japanese-english-dictionary) ([GitHub repo](https://github.com/janclarin/jisho-alfred-workflow)) by [janclarin](http://www.packal.org/users/janclarin) ([on GitHub](https://github.com/janclarin/)).
  Easily and quickly search Jisho.org, a powerful Japanese-English dictionary.
- [jQueryApiCN](http://www.packal.org/workflow/jqueryapicn) ([GitHub repo](https://github.com/kennylee26/alfred-jquery-api-cn)) by [kennylee](http://www.packal.org/users/kennylee) ([on GitHub](https://github.com/kennylee26/)).
  jQuery中文API手册.
- [Julian Date calculator](http://www.packal.org/workflow/julian-date-calculator) ([GitHub repo](https://github.com/Tam-Lin/julian_date)) by [Tam-Lin](http://www.packal.org/users/tam-lin) ([on GitHub](https://github.com/Tam-Lin/)).
  Converts dates to/from Julian dates, as well as some date math.
- [KA Torrents](http://www.packal.org/workflow/ka-torrents) by [hackademic](http://www.packal.org/users/hackademic).
  Search and download torrents from kickass.so.
- [Karabiner Elements Profile Switcher](http://www.packal.org/workflow/karabiner-elements-profile-switcher) ([GitHub repo](https://github.com/awinecki/karabiner-elements-profile-switcher)) by [awinecki](http://www.packal.org/users/awinecki) ([on GitHub](https://github.com/awinecki/)).
  Easily switch selected profile as configured in ~/.config/karabiner/karabiner.json.
- [KAT Search](http://www.packal.org/workflow/kat-search) by [emamuna](http://www.packal.org/users/emamuna).
  Just a workflow used to search on KAT (KickAssTorrent) website.
- [KAT search to Transmission](http://www.packal.org/workflow/kat-search-transmission) by [auino](http://www.packal.org/users/auino).
  Workflow used to search torrent files on KAT mirrors and download chosen files through a remote Transmission server.
- [Kitap Metre](http://www.packal.org/workflow/kitap-metre) ([GitHub repo](https://github.com/ttuygun/alfred-kitap-metre-workflow)) by [ttuygun](http://www.packal.org/users/ttuygun) ([on GitHub](https://github.com/ttuygun/)).
  This alfred workflow shows kitapmetre.com's (the best book price search engine) results.
- [Laser SSH](http://www.packal.org/workflow/laser-ssh) by [paperElectron](http://www.packal.org/users/paperelectron).
  Choose SSH connection from filterable list.
- [LastPass Vault Manager](http://www.packal.org/workflow/lastpass-vault-manager) ([GitHub repo](https://github.com/bachya/lp-vault-manager)) by [bachya](http://www.packal.org/users/bachya) ([on GitHub](https://github.com/bachya/)).
  A workflow to interact with a LastPass vault.
- [LibGen](http://www.packal.org/workflow/libgen) ([GitHub repo](https://github.com/smargh/alfred_libgen)) by [hackademic](http://www.packal.org/users/hackademic) ([on GitHub](https://github.com/smargh/)).
  Search and Download pdfs and ebooks from Library Genesis.
- [logtivly](http://www.packal.org/workflow/logtivly) ([GitHub repo](https://github.com/lobolabs/logtivly-alfred)) by [abbood](http://www.packal.org/users/abbood) ([on GitHub](https://github.com/lobolabs/)).
  log your hours on google sheets using alfred! see https://www.youtube.com/watch?v=XAAXoTbIZ5E.
- [MailTo](http://www.packal.org/workflow/mailto) ([GitHub repo](https://github.com/deanishe/alfred-mailto)) by [deanishe](http://www.packal.org/users/deanishe) ([on GitHub](https://github.com/deanishe/)).
  Send mail to contacts and groups from your Address Book.
- [MangaEden Search](http://www.packal.org/workflow/mangaeden-search) by [emamuna](http://www.packal.org/users/emamuna).
  Search, read and download manga from mangaeden.com.
- [Mathematica](http://www.packal.org/workflow/mathematica) by [sam-marsh](http://www.packal.org/users/sam-marsh).
  Runs commands using the Mathematica kernel.
- [Mianliao](http://www.packal.org/workflow/mianliao) ([GitHub repo](https://github.com/whtsky/Alfred-Mianliao)) by [whtsky](http://www.packal.org/users/whtsky) ([on GitHub](https://github.com/whtsky/)).
  Help you log into Mianliao Network.
- [moment](http://www.packal.org/workflow/moment) ([GitHub repo](https://github.com/perfectworks/alfred-workflow-moment)) by [perfectworks](http://www.packal.org/users/perfectworks) ([on GitHub](https://github.com/perfectworks/)).
  Advanced time utility.
- [Movie and TV Show Search](http://www.packal.org/workflow/movie-and-tv-show-search) ([GitHub repo](https://github.com/tmcknight/Movie-and-TV-Show-Search-Alfred-Workflow)) by [tone](http://www.packal.org/users/tone) ([on GitHub](https://github.com/tmcknight/)).
  Search for movies and tv shows to find ratings from a few sites.
- [Movie Ratings](http://www.packal.org/workflow/movie-ratings) ([GitHub repo](https://github.com/mattsson/movies-ratings-alfred)) by [mattsson](http://www.packal.org/users/mattsson) ([on GitHub](https://github.com/mattsson/)).
  Search for a movie and see its IMDb, Rotten Tomatoes and Metacritic ratings.
- [Network Location](http://www.packal.org/workflow/network-location) ([GitHub repo](https://github.com/deanishe/alfred-network-location)) by [deanishe](http://www.packal.org/users/deanishe) ([on GitHub](https://github.com/deanishe/)).
  List, filter and activate network locations from within Alfred.
- [NpmSearch](http://www.packal.org/workflow/npmsearch) ([GitHub repo](https://github.com/ycjcl868/alfred-npmjs)) by [ycjcl868](http://www.packal.org/users/ycjcl868) ([on GitHub](https://github.com/ycjcl868/)).
  npm packages quick search.
- [NyaaSearch](http://www.packal.org/workflow/nyaasearch) ([GitHub repo](https://github.com/Ankirama/alfred-workflows/tree/master/NyaaSearch)) by [Ankirama](http://www.packal.org/users/ankirama) ([on GitHub](https://github.com/Ankirama/)).
  Search torrents on nyaa and download/copy it.
- [Openhab](http://www.packal.org/workflow/openhab) ([GitHub repo](https://github.com/digitalbirdo/alfred-openhab-workflow)) by [DigitalBird](http://www.packal.org/users/digitalbird) ([on GitHub](https://github.com/digitalbirdo/)).
  Control your Openhab Smart Home with Alfred.
- [Order of Magnituce](http://www.packal.org/workflow/order-magnitude) by [tdhopper](http://www.packal.org/users/tdhopper).
  Convert a number to natural language (rounded to any number of places).
- [Packal Workflow Search](http://www.packal.org/workflow/packal-workflow-search) ([GitHub repo](https://github.com/deanishe/alfred-packal-search)) by [deanishe](http://www.packal.org/users/deanishe) ([on GitHub](https://github.com/deanishe/)).
  Search Packal.org from the comfort of Alfred.
- [Pandoctor](http://www.packal.org/workflow/pandoctor) ([GitHub repo](https://github.com/smargh/alfred_pandoctor)) by [hackademic](http://www.packal.org/users/hackademic) ([on GitHub](https://github.com/smargh/)).
  An Alfred GUI for Pandoc.
- [Parsers](http://www.packal.org/workflow/parsers) ([GitHub repo](https://github.com/smargh/alfred_parsers)) by [hackademic](http://www.packal.org/users/hackademic) ([on GitHub](https://github.com/smargh/)).
  Greek and Latin parsers.
- [pass](http://www.packal.org/workflow/pass) ([GitHub repo](https://github.com/MatthewWest/pass-alfred/)) by [mwest](http://www.packal.org/users/mwest) ([on GitHub](https://github.com/MatthewWest/)).
  Provide a minimal wrapper over the pass password manager (passwordstore.org).
- [Percent Change](http://www.packal.org/workflow/percent-change) ([GitHub repo](https://github.com/bradmontgomery/alfred-percent-change)) by [bkmontgomery](http://www.packal.org/users/bkmontgomery) ([on GitHub](https://github.com/bradmontgomery/)).
  Easily do percentage calculations.
- [PERT Calculator](http://www.packal.org/workflow/pert-calculator) by [agileadam](http://www.packal.org/users/agileadam).
  Generates accurate time estimates based on optimistic, realistic, and pessimistic expectations.
- [PHPStorm project opener ](http://www.packal.org/workflow/phpstorm-project-opener) ([GitHub repo](https://github.com/hansdubois/aflfred-phpstorm-opener)) by [hansdubois](http://www.packal.org/users/hansdubois) ([on GitHub](https://github.com/hansdubois/)).
  PHPStorm project opener.
- [Pocket for Alfred](http://www.packal.org/workflow/pocket-alfred) ([GitHub repo](https://github.com/fniephaus/alfred-pocket)) by [fniephaus](http://www.packal.org/users/fniephaus) ([on GitHub](https://github.com/fniephaus/)).
  Manage your Pocket list with Alfred.
- [Pomodoro Alfred](https://github.com/ecbrodie/pomodoro-alfred) by [Evan Brodie](https://github.com/ecbrodie) ([on GitHub](https://github.com/ecbrodie/)).
  Track Pomodoros through Alfred.
- [Powerthesaurus Search](http://www.packal.org/workflow/powerthesaurus-search) ([GitHub repo](https://github.com/clarencecastillo/alfred-powerthesaurus)) by [clarencecastillo](http://www.packal.org/users/clarencecastillo) ([on GitHub](https://github.com/clarencecastillo/)).
  Search Powerthesaurus synonyms and antonyms from Alfred.
- [Product Hunt](http://www.packal.org/workflow/product-hunt) ([GitHub repo](https://github.com/loris/alfred-producthunt-workflow)) by [loris](http://www.packal.org/users/loris) ([on GitHub](https://github.com/loris/)).
  List Product Hunt today's hunts.
- [ProductHunt](http://www.packal.org/workflow/producthunt) ([GitHub repo](https://github.com/chiefy/ph-workflow)) by [chiefy](http://www.packal.org/users/chiefy) ([on GitHub](https://github.com/chiefy/)).
  Read ProductHunt in Alfred.
- [Progress Bar](http://www.packal.org/workflow/progress-bar) ([GitHub repo](https://github.com/jeeftor/ProgressBar)) by [jeffsui](http://www.packal.org/users/jeffsui) ([on GitHub](https://github.com/jeeftor/)).
  Sample progress bar workflow.
- [PWS History](http://www.packal.org/workflow/pws-history) ([GitHub repo](https://github.com/hrbrmstr/alfred-pws)) by [hrbrmstr](http://www.packal.org/users/hrbrmstr) ([on GitHub](https://github.com/hrbrmstr/)).
  Retrieve personal weather station history from Weather Underground.
- [Python Interpreter](http://www.packal.org/workflow/python-interpreter) ([GitHub repo](https://github.com/altre/alfred_python_interpreter)) by [altre](http://www.packal.org/users/altre) ([on GitHub](https://github.com/altre/)).
  Use python interpreter directly from alfred.
- [quick command for alfred workflow 2 ](http://www.packal.org/workflow/quick-command-alfred-workflow-2) ([GitHub repo](https://github.com/albertxavier001/alfred-workflow-quick-command)) by [albertxavier](http://www.packal.org/users/albertxavier) ([on GitHub](https://github.com/albertxavier001/)).
  Copy, run, generate, del your custom commands.
- [Quick Stocks](http://www.packal.org/workflow/quick-stocks) by [paperElectron](http://www.packal.org/users/paperelectron).
  Add some stock symbols for Alfred to check for you.
- [Quip](http://www.packal.org/workflow/quip) ([GitHub repo](https://github.com/orf/alfred-quip-workflow)) by [orf](http://www.packal.org/users/orf) ([on GitHub](https://github.com/orf/)).
  Search Quip documents from within Alfred.
- [Radar](http://www.packal.org/workflow/radar) ([GitHub repo](https://github.com/amoose136/radar/)) by [amoose136](http://www.packal.org/users/amoose136) ([on GitHub](https://github.com/amoose136/)).
  Show animated doppler radar for local area using quicklook. (US only for now).
- [Ramda Docs](http://www.packal.org/workflow/ramda-docs) ([GitHub repo](https://github.com/raine/alfred-ramda-workflow)) by [raine](http://www.packal.org/users/raine) ([on GitHub](https://github.com/raine/)).
  Search Ramda documentation.
- [Rates](http://www.packal.org/workflow/rates) ([GitHub repo](https://github.com/kennedyoliveira/alfred-rates)) by [Kennedy Oliveira](http://www.packal.org/users/kennedy-oliveira) ([on GitHub](https://github.com/kennedyoliveira/)).
  Simple exchange rates for alfred.
- [raywenderlich](http://www.packal.org/workflow/raywenderlich) ([GitHub repo](https://github.com/softdevstory/alfred-workflows/tree/master/raywenderlich)) by [softdevstory](http://www.packal.org/users/softdevstory) ([on GitHub](https://github.com/softdevstory/)).
  Display the recent ariticles from raywenderlich.com.
- [Readability for Alfred](http://www.packal.org/workflow/readability-alfred) ([GitHub repo](https://github.com/fniephaus/alfred-readability/)) by [fniephaus](http://www.packal.org/users/fniephaus) ([on GitHub](https://github.com/fniephaus/)).
  Manage your Readability list with Alfred.
- [Reddit](http://www.packal.org/workflow/reddit) ([GitHub repo](https://github.com/deanishe/alfred-reddit)) by [deanishe](http://www.packal.org/users/deanishe) ([on GitHub](https://github.com/deanishe/)).
  Browse Reddit from Alfred.
- [Relative Dates](http://www.packal.org/workflow/relative-dates) ([GitHub repo](https://github.com/deanishe/alfred-relative-dates)) by [deanishe](http://www.packal.org/users/deanishe) ([on GitHub](https://github.com/deanishe/)).
  Generate relative dates based on a simple input format.
- [Resolve URL](http://www.packal.org/workflow/resolve-url) ([GitHub repo](https://github.com/deanishe/alfred-resolve-url)) by [deanishe](http://www.packal.org/users/deanishe) ([on GitHub](https://github.com/deanishe/)).
  Follows any HTTP redirects and returns the canonical URL. Also displays information about the primary host (hostname, IP address(es), aliases).
- [RGB to Hex](http://www.packal.org/workflow/rgb-hex) ([GitHub repo](https://github.com/sonicwu/alfred-rgb2hex)) by [Sonic Wu](http://www.packal.org/users/sonic-wu) ([on GitHub](https://github.com/sonicwu/)).
  Convert RGB values of a color to a hexadecimal string.
- [Rotten Search](http://www.packal.org/workflow/rotten-search) ([GitHub repo](https://github.com/mrz1277/alfred-workflows/tree/master/net.yakiyama.alfred.rotten)) by [yakiyama](http://www.packal.org/users/yakiyama) ([on GitHub](https://github.com/mrz1277/)).
  Search movie from RottenTomatoes.com.
- [Ruter workflow for Alfred](http://www.packal.org/workflow/ruter-workflow-alfred) ([GitHub repo](https://github.com/kimsyversen/Ruter-workflow-for-Alfred)) by [kimsyversen](http://www.packal.org/users/kimsyversen) ([on GitHub](https://github.com/kimsyversen/)).
  Plan your trips directly from Alfred.
- [Safari History Search](http://www.packal.org/workflow/safari-history-search-0) ([GitHub repo](https://github.com/rx2130/alfred-safari-history-search/)) by [rx2130](http://www.packal.org/users/rx2130) ([on GitHub](https://github.com/rx2130/)).
  Search Safari Browse History from Alfred.
- [Say it with GIFs](http://www.packal.org/workflow/say-it-gifs) ([GitHub repo](https://github.com/deanishe/alfred-gifs)) by [deanishe](http://www.packal.org/users/deanishe) ([on GitHub](https://github.com/deanishe/)).
  Browse your horde of GIFs and get their URLs.
- [Search in Salesforce](http://www.packal.org/workflow/search-salesforce) ([GitHub repo](https://github.com/jereze/alfred-salesforce)) by [jereze](http://www.packal.org/users/jereze) ([on GitHub](https://github.com/jereze/)).
  Search in Salesforce from your Mac.
- [Search Omnifocus](http://www.packal.org/workflow/search-omnifocus) ([GitHub repo](https://github.com/rhydlewis/search-omnifocus)) by [rhyd](http://www.packal.org/users/rhyd) ([on GitHub](https://github.com/rhydlewis/)).
  This is a workflow that performs free text searches on OmniFocus data.
- [Search Terminal history](http://www.packal.org/workflow/search-terminal-history) by [N00bDaan](http://www.packal.org/users/n00bdaan).
  Search Terminal history and copy command to clipboard for quick adjustment/reuse.
- [Searchio!](http://www.packal.org/workflow/searchio) ([GitHub repo](https://github.com/deanishe/alfred-searchio)) by [deanishe](http://www.packal.org/users/deanishe) ([on GitHub](https://github.com/deanishe/)).
  Auto-suggest search results from multiple search engines and languages.
- [Secure Password Generator](http://www.packal.org/workflow/secure-password-generator) ([GitHub repo](https://github.com/deanishe/alfred-pwgen)) by [deanishe](http://www.packal.org/users/deanishe) ([on GitHub](https://github.com/deanishe/)).
  Generate secure random passwords from Alfred. Uses /dev/urandom as source of entropy.
- [SEND](http://www.packal.org/workflow/send) by [hackademic](http://www.packal.org/users/hackademic).
  Send documents to the cloud.
- [Seq-utilies](http://www.packal.org/workflow/seq-utilities) ([GitHub repo](https://github.com/danielecook/seq-utilities)) by [danielecook](http://www.packal.org/users/danielecook) ([on GitHub](https://github.com/danielecook/)).
  Fetch complement, reverse complement, RNA, and protein sequences. Generate random DNA. Blast a sequence.
- [Shell Variables](http://www.packal.org/workflow/shell-variables) ([GitHub repo](https://github.com/hug33k/Alfred-ShellVariables)) by [hug33k](http://www.packal.org/users/hug33k) ([on GitHub](https://github.com/hug33k/)).
  Get your shell's variables into Alfred.
- [Simple Timer](http://www.packal.org/workflow/simple-timer) by [Paul Eunjae Lee](http://www.packal.org/users/paul-eunjae-lee).
  A very simple timer.
- [Skimmer](http://www.packal.org/workflow/skimmer) ([GitHub repo](https://github.com/smargh/alfred-Skimmer)) by [hackademic](http://www.packal.org/users/hackademic) ([on GitHub](https://github.com/smargh/)).
  Actions for PDF viewer Skim.
- [slackfred](http://www.packal.org/workflow/slackfred) ([GitHub repo](https://github.com/fspinillo/slackfred)) by [frankspin](http://www.packal.org/users/frankspin) ([on GitHub](https://github.com/fspinillo/)).
  Interact with the chat service Slack via Alfred (multi-org supported).
- [Smart Folders](http://www.packal.org/workflow/smart-folders) ([GitHub repo](https://github.com/deanishe/alfred-smartfolders)) by [deanishe](http://www.packal.org/users/deanishe) ([on GitHub](https://github.com/deanishe/)).
  View and explore your Smart Folders (Saved Searches).
- [Snippets](http://www.packal.org/workflow/snippets) ([GitHub repo](https://github.com/smargh/alfred_snippets)) by [hackademic](http://www.packal.org/users/hackademic) ([on GitHub](https://github.com/smargh/)).
  Simple, document-specific text snippets.
- [SONOS Controller](http://www.packal.org/workflow/sonos-controller) by [fns720](http://www.packal.org/users/fns720).
  Basic controls for SONOS speakers.
- [Sourcegraph](http://www.packal.org/workflow/sourcegraph) ([GitHub repo](https://github.com/sourcegraph/sourcegraph-alfred)) by [rohanpai](http://www.packal.org/users/rohanpai) ([on GitHub](https://github.com/sourcegraph/)).
  Sourcegraph Alfred Workflow.
- [Splatoon](http://www.packal.org/workflow/splatoon) ([GitHub repo](https://github.com/flipxfx/alfred-splatoon)) by [flipxfx](http://www.packal.org/users/flipxfx) ([on GitHub](https://github.com/flipxfx/)).
  A workflow with Splatoon helpers (maps, wiki).
- [Spritzr](http://www.packal.org/workflow/spritzr) ([GitHub repo](https://github.com/smargh/alfred_spritzr)) by [hackademic](http://www.packal.org/users/hackademic) ([on GitHub](https://github.com/smargh/)).
  An Alfred Speed-Reader.
- [Stack Overflow](http://www.packal.org/workflow/stack-overflow) ([GitHub repo](https://github.com/Que3216/alfred-stack-overflow)) by [Que3216](http://www.packal.org/users/que3216) ([on GitHub](https://github.com/Que3216/)).
  Get answers to simple questions like "python function syntax", without having to open your web browser.
- [StackOverflow Search](http://www.packal.org/workflow/stackoverflow-search) ([GitHub repo](https://github.com/deanishe/alfred-stackoverflow)) by [deanishe](http://www.packal.org/users/deanishe) ([on GitHub](https://github.com/deanishe/)).
  Search StackOverflow.com from Alfred.
- [Star Ratings](http://www.packal.org/workflow/star-ratings) ([GitHub repo](https://github.com/deanishe/alfred-star-ratings)) by [deanishe](http://www.packal.org/users/deanishe) ([on GitHub](https://github.com/deanishe/)).
  View and set ratings for your files and folders.
- [Status](http://www.packal.org/workflow/status) ([GitHub repo](https://github.com/ekonstantinidis/alfred-status-workflow)) by [iamemmanouil](http://www.packal.org/users/iamemmanouil) ([on GitHub](https://github.com/ekonstantinidis/)).
  Alfred workflow that displays status of well known services like GitHub, Twitter and more.
- [Steam](http://www.packal.org/workflow/steam) by [tresni](http://www.packal.org/users/tresni).
  Activate your Steam codes & launch steam games with a quick keystroke or keyword.
- [Sublime Text Projects](http://www.packal.org/workflow/sublime-text-projects) ([GitHub repo](https://github.com/deanishe/alfred-sublime-text)) by [deanishe](http://www.packal.org/users/deanishe) ([on GitHub](https://github.com/deanishe/)).
  View, filter and open your Sublime Text (2 and 3) project files.
- [SwitchHosts!](http://www.packal.org/workflow/switchhosts) ([GitHub repo](https://github.com/oldj/SwitchHosts)) by [oldj](http://www.packal.org/users/oldj) ([on GitHub](https://github.com/oldj/)).
  The workflow for SwitchHosts! app.
- [TeXdoc](http://www.packal.org/workflow/texdoc) ([GitHub repo](https://github.com/egeerardyn/alfred-texdoc)) by [Egon Geerardyn](http://www.packal.org/users/egon-geerardyn) ([on GitHub](https://github.com/egeerardyn/)).
  Searches your LaTeX documentation using texdoc.
- [TodoList](https://github.com/ecmadao/Alfred-TodoList) by [ecmadao](https://github.com/ecmadao) ([on GitHub](https://github.com/ecmadao/)).
  A simple todo-workflow lets you add, complete or delete todo in to-do lists.
- [Torrent](http://www.packal.org/workflow/torrent) ([GitHub repo](https://github.com/bfw/alfred-torrent)) by [bfw](http://www.packal.org/users/bfw) ([on GitHub](https://github.com/bfw/)).
  Search for torrents, choose among the results in Alfred and start the download in uTorrent.
- [Translate Workflow - use Google or Microsoft Translate](http://www.packal.org/workflow/translate-workflow-use-google-or-microsoft-translate) ([GitHub repo](https://github.com/pbojkov/alfred-workflow-google-translate)) by [rustycamper](http://www.packal.org/users/rustycamper) ([on GitHub](https://github.com/pbojkov/)).
  Translate words or phrases using Google or Microsoft Translate.
- [Travis CI for Alfred](http://www.packal.org/workflow/travis-ci-alfred) by [fniephaus](http://www.packal.org/users/fniephaus).
  Quickly check build statuses on travis-ci.org.
- [Ulysses](http://www.packal.org/workflow/ulysses) ([GitHub repo](https://github.com/robwalton/alfred-ulysses-workflow)) by [robwalton](http://www.packal.org/users/robwalton) ([on GitHub](https://github.com/robwalton/)).
  Open groups or sheets in Ulysses.
- [URL craft](http://www.packal.org/workflow/url-craft) by [takanabe](http://www.packal.org/users/takanabe).
  A workflow that transforms a url into new one that allows some formats such as "Github Flavored Markdown link" or "shorten url" and so on.
- [VagrantUP](http://www.packal.org/workflow/vagrantup) ([GitHub repo](https://github.com/m1keil/alfred-vagrant-workflow)) by [m1keil](http://www.packal.org/users/m1keil) ([on GitHub](https://github.com/m1keil/)).
  List and control Vagrant environments with Alfred2/3.
- [Viscosity VPN Manager](http://www.packal.org/workflow/viscosity-vpn-manager) ([GitHub repo](https://github.com/deanishe/alfred-viscosity)) by [deanishe](http://www.packal.org/users/deanishe) ([on GitHub](https://github.com/deanishe/)).
  Manage Viscosity VPN connections.
- [VM Control](http://www.packal.org/workflow/vm-control) ([GitHub repo](https://github.com/fniephaus/alfred-vmcontrol)) by [fniephaus](http://www.packal.org/users/fniephaus) ([on GitHub](https://github.com/fniephaus/)).
  Control your Parallels and Virtual Box virtual machines.
- [VPN Switch](http://www.packal.org/workflow/vpn-switch) ([GitHub repo](https://github.com/flyeek/vpn-switch)) by [flyeek](http://www.packal.org/users/flyeek) ([on GitHub](https://github.com/flyeek/)).
  Switch VPN on/off.
- [Wikify](http://www.packal.org/workflow/wikify) ([GitHub repo](https://github.com/smargh/alfred_EN-Wikify)) by [hackademic](http://www.packal.org/users/hackademic) ([on GitHub](https://github.com/smargh/)).
  Your little Evernote Wiki-Helper.
- [Workflow Directory - Open in Finder or Terminal](http://www.packal.org/workflow/workflow-directory-open-finder-or-terminal) ([GitHub repo](https://github.com/jeeftor/AlfredWorkflowDirectory)) by [jeffsui](http://www.packal.org/users/jeffsui) ([on GitHub](https://github.com/jeeftor/)).
  Same behavior as the right click menu on a workflow.  Saves you time if you are developing workflows.
- [Workon Virtualenv](http://www.packal.org/workflow/workon-virtualenv) ([GitHub repo](https://github.com/johnnycakes79/alfred-workon-virtualenv)) by [johnnycakes79](http://www.packal.org/users/johnnycakes79) ([on GitHub](https://github.com/johnnycakes79/)).
  Workflow to list and start python virtualenvs (assumes you and have virtualenv and virtualenvwrapper installed).
- [Wowhead](http://www.packal.org/workflow/wowhead) ([GitHub repo](https://github.com/owenwater/alfred-wowhead)) by [owenwater](http://www.packal.org/users/owenwater) ([on GitHub](https://github.com/owenwater/)).
  An Alfred workflow that helps you search World of Warcraft® database provided by wowhead.com.
- [Wunderlist Workflow for Alfred](http://www.packal.org/workflow/wunderlist-workflow-alfred) ([GitHub repo](https://github.com/idpaterson/alfred-wunderlist-workflow)) by [ipaterson](http://www.packal.org/users/ipaterson) ([on GitHub](https://github.com/idpaterson/)).
  Unbelievably fast entry for tasks with due dates, reminders, and recurrence in Wunderlist.
- [Wunderlist3.alfredworkflow](http://www.packal.org/workflow/wunderlist3alfredworkflow) ([GitHub repo](https://github.com/camgnostic/Wunderlist-3-Alfred)) by [gnostic](http://www.packal.org/users/gnostic) ([on GitHub](https://github.com/camgnostic/)).
  A Wunderlist 3 API cloud-based alfred workflow.
- [Youdao Dict](http://www.packal.org/workflow/youdao-dict) ([GitHub repo](https://github.com/liszd/whyliam.workflows.youdao/releases)) by [WhyLiam](http://www.packal.org/users/whyliam) ([on GitHub](https://github.com/liszd/)).
  使用有道翻译你想知道的单词和语句.
- [Youtrack - create issues](http://www.packal.org/workflow/youtrack-create-issues) ([GitHub repo](https://github.com/altryne/youtrack_alfred)) by [altryne](http://www.packal.org/users/altryne) ([on GitHub](https://github.com/altryne/)).
  Creates issues in Your Youtrack installation.
- [Zebra](http://www.packal.org/workflow/zebra) ([GitHub repo](https://github.com/rsnts/alfred-zebra)) by [rsnts](http://www.packal.org/users/rsnts) ([on GitHub](https://github.com/rsnts/)).
  Alfred worflow for Zebra interaction.
- [ZotQuery](http://www.packal.org/workflow/zotquery) ([GitHub repo](https://github.com/smargh/alfred_zotquery)) by [hackademic](http://www.packal.org/users/hackademic) ([on GitHub](https://github.com/smargh/)).
  Search Zotero. From the Comfort of Your Keyboard.
- [彩云天气](http://www.packal.org/workflow/cai-yun-tian-qi) ([GitHub repo](https://github.com/wangkezun/cytq)) by [Marvin](http://www.packal.org/users/marvin) ([on GitHub](https://github.com/wangkezun/)).
  通过彩云天气API接口获取天气预报.





[alfred]: http://www.alfredapp.com/
[awv2]: https://github.com/deanishe/alfred-workflow/tree/v2
[alabaster]: https://github.com/bitprophet/alabaster
[bitprophet]: https://github.com/bitprophet
[cc]: https://creativecommons.org/licenses/by-nc/4.0/legalcode
[coveralls]: https://coveralls.io/r/deanishe/alfred-workflow?branch=master
[deanishe]: https://github.com/deanishe
[docs-api]: http://www.deanishe.net/alfred-workflow/#api-documentation
[docs-rtd]: https://alfredworkflow.readthedocs.org/
[docs]: http://www.deanishe.net/alfred-workflow/
[dash]: https://github.com/deanishe/alfred-workflow/raw/master/docs/Alfred-Workflow.docset.zip
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
[shield-download]: https://img.shields.io/pypi/dm/Alfred-Workflow.svg?style=flat
[shield-health]: https://landscape.io/github/deanishe/alfred-workflow/master/landscape.png?style=flat
[shield-licence]: https://pypip.in/license/Alfred-Workflow/badge.svg?style=flat
[shield-status]: https://img.shields.io/pypi/status/Alfred-Workflow.svg?style=flat
[shield-travis]: https://travis-ci.org/deanishe/alfred-workflow.svg?branch=master&style=flat
[shield-version]: https://img.shields.io/pypi/v/Alfred-Workflow.svg?style=flat
[shield-pyversions]: https://img.shields.io/pypi/pyversions/Alfred-Workflow.svg?style=flat
[smargh]: https://github.com/smargh
[sphinx]: http://sphinx-doc.org/
[travis]: https://travis-ci.org/deanishe/alfred-workflow
[cheeseshop]: https://pypi.python.org/pypi
[pip-docs]: https://pip.pypa.io/en/latest/
[ruby-template]: http://zhaocai.github.io/alfred2-ruby-template/
[python-keyring]: https://pypi.python.org/pypi/keyring
