#!/usr/bin/env python
# encoding: utf-8
#
# Copyright © 2014 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-02-15
#

"""
Python helper libraries for `Alfred 2 <http://www.alfredapp.com/>`_ Workflow
authors.

Provides convenience methods for:

- Parsing script arguments.
- Text decoding/normalisation.
- Caching data and settings.
- Secure storage (and sync) of passwords (using OS X Keychain).
- Generating XML output for Alfred.
- Including external libraries (adding directories to ``sys.path``).
- Filtering results using an Alfred-like algorithm.
- Generating log output for debugging.
- Capturing errors, so the workflow doesn't fail silently.

Quick Example
=============

Show recent Pinboard.in posts in Alfred. Create a **Script Filter** with
Language ``/usr/bin/python`` and paste the following into the **Script** field::

    import sys
    from workflow import Workflow, ICON_WEB, web

    API_KEY = 'your-api-key'

    def main(wf):
        url = 'https://api.pinboard.in/v1/posts/recent'
        params = dict(auth_token=API_KEY, count=20, format='json')
        r = web.get(url, params)
        r.raise_for_status()
        for post in r.json()['posts']:
            wf.add_item(post['description'], post['href'], arg=post['href'],
                        uid=post['hash'], valid=True, icon=ICON_WEB)
        wf.send_feedback()


    if __name__ == u"__main__":
        wf = Workflow()
        sys.exit(wf.run(main))

"""

__version__ = '1.0'

from .workflow import Workflow
from .workflow import (ICON_ERROR, ICON_WARNING, ICON_NOTE, ICON_INFO,
                       ICON_FAVORITE, ICON_FAVOURITE, ICON_USER, ICON_GROUP,
                       ICON_HELP, ICON_NETWORK, ICON_WEB, ICON_COLOR,
                       ICON_COLOUR, ICON_SYNC, ICON_SETTINGS, ICON_TRASH,
                       ICON_MUSIC, ICON_BURN, ICON_ACCOUNT, ICON_ERROR)
