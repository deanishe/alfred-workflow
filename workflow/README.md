
# Alfred-Workflow #

## New behaviour ##

- Version must now be in a `version` file
- Removed `workflow.Workflow.alfred_env`. Everything is now in `workflow.env`
- 

## Layout ##

### `__init__.py` ###

- [ ] `Workflow` class

Main class

### `background.py` ###

Run scripts in the background.

- [x] Change logging.
- [x] Remove `Workflow` if possible

### `base.py` ###

Logging, data models, constants.

- [ ] 

### `_env.py` and `env.py` ###

Workflow variables from `info.plist` and environment.

- [ ] 

### `feedback.py` ###

XML generation. Future home for AppleScript dialogs?

- [ ] 

### `hooks.py` ###

Attachment points for plugins.

- [ ] Attachment for serializers
- [ ] Attachment for updaters
- [ ] Attachment for magic args
- [ ] Attachment for XML post-processor

### `icons.py` ###

Namespace for system icon paths.

### `plugins.py` ###

Simple plugin loader and manager.

- [ ] GitHub updater
- [ ] Default magic args
- [ ] Default serializers

### `search.py` ###

Where data filtering functions live.

### `storage.py` ###

Persisent storage APIs. Data & cache directories, Keychain.

- [ ] Data storage API
- [ ] Cache storage API
- [ ] Keychain API

### `update.py` ###

Update manager and plugin superclass.

- [ ] Complete manager
- [ ] GitHub plugin

### `util.py` ###

Helper functions.

- [ ] 

### `web.py` ###

HTTP library.

- [ ] Cookie support? (Probably requires sessions)

### `workflow.py` ###

Legacy module. Probably to be removed.

#### Workflow ####

- [ ] Move data/caching code to `storage.py`
- [ ] Move serializers to `storage.py` and plugins
- [ ] Replace `alfred_env` and `info` with `env`
