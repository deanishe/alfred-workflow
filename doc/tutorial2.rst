.. _tutorial2:

==============================
Building a user-ready Workflow
==============================

In which we create a `Pinboard.in <https://pinboard.in/>`_ Workflow ready for
the masses.

In the :ref:`first part <tutorial>` of the tutorial, we built a useable Workflow
to view, search and open your recent Pinboard posts. The Workflow isn't quite
ready to be distributed to other users however: we can't expect them to go
grubbing around in the source code, changing constants like an animal to set
their own API key.

What's more, an update to the Workflow would overwrite their changes.

So now we're going to edit the Workflow so users can add their API key from the
comfort of Alfred's friendly query box and use :attr:`~workflow.workflow.Workflow.settings`
to save it in the Workflow's data directory where it won't get overwritten.


Performing multiple actions from one script
-------------------------------------------

To set the user's API key, we're going to need a new action. We could write a
second script to do this, but we're going to stick with one script and make it
smart enough to do two things, instead. The advantage of using one script is
that if you build a workflow with lots of actions, you don't have a dozen or more
scripts to manage.

We'll start by adding an argument parser (using :mod:`argparse`) to ``main`` and some
``if``-statements to alter the script behaviour depending on the arguments passed
to the script.

.. code-block:: python
   :emphasize-lines: 5,8-15,39-89

    # encoding: utf-8

    import sys
    import argparse
    from workflow import Workflow, ICON_WEB, ICON_WARNING, web


    def get_recent_posts(api_key):
        """Retrieve recent posts from Pinboard.in

        Returns a list of post dictionaries.

        """
        url = 'https://api.pinboard.in/v1/posts/recent'
        params = dict(auth_token=api_key, count=100, format='json')
        r = web.get(url, params)

        # throw an error if request failed
        # Workflow will catch this and show it to the user
        r.raise_for_status()

        # Parse the JSON returned by pinboard and extract the posts
        result = r.json()
        posts = result['posts']
        return posts


    def search_key_for_post(post):
        """Generate a string search key for a post"""
        elements = []
        elements.append(post['description'])  # title of post
        elements.append(post['tags'])  # post tags
        elements.append(post['extended'])  # description
        return u' '.join(elements)


    def main(wf):

        # build argument parser to parse script args and collect their
        # values
        parser = argparse.ArgumentParser()
        # add an optional (nargs='?') --setkey argument and save its
        # value to 'apikey' (dest). This will be called from a separate "Run Script"
        # action with the API key
        parser.add_argument('--setkey', dest='apikey', nargs='?', default=None)
        # add an optional query and save it to 'query'
        parser.add_argument('query', nargs='?', default=None)
        # parse the script's arguments
        args = parser.parse_args(wf.args)

        ####################################################################
        # Save the provided API key
        ####################################################################

        # decide what to do based on arguments
        if args.apikey:  # Script was passed an API key
            # save the key
            wf.settings['api_key'] = args.apikey
            return 0  # 0 means script exited cleanly

        ####################################################################
        # Check that we have an API key saved
        ####################################################################

        api_key = wf.settings.get('api_key', None)
        if not api_key:  # API key has not yet been set
            wf.add_item('No API key set.',
                        'Please use pbsetkey to set your Pinboard API key.',
                        valid=False,
                        icon=ICON_WARNING)
            wf.send_feedback()
            return 0

        ####################################################################
        # View/filter Pinboard posts
        ####################################################################

        query = args.query
        # Retrieve posts from cache if available and no more than 600
        # seconds old

        def wrapper():
            """`cached_data` can only take a bare callable (no args),
            so we need to wrap callables needing arguments in a function
            that needs none.
            """
            return get_recent_posts(api_key)

        posts = wf.cached_data('posts', wrapper, max_age=600)

        # If script was passed a query, use it to filter posts
        if query:
            posts = wf.filter(query, posts, key=search_key_for_post)

        # Loop through the returned posts and add a item for each to
        # the list of results for Alfred
        for post in posts:
            wf.logger.debug(post)
            wf.add_item(title=post['description'],
                        subtitle=post['href'],
                        arg=post['href'],
                        valid=True,
                        icon=ICON_WEB)

        # Send the results to Alfred as XML
        wf.send_feedback()
        return 0


    if __name__ == u"__main__":
        wf = Workflow()
        sys.exit(wf.run(main))



Quite a lot has happened here: at the top, we're importing a couple more icons
that we use in ``main`` to notify the user that their API key is missing and
that they should set it.

We've adapted ``get_recent_posts`` to accept an ``api_key`` argument. We *could*
continue to use the ``API_KEY`` global variable, but that's considered bad form.

As a result of this, we've had to alter the way
:meth:`~workflow.workflow.Workflow.cached_data` is called. It can't call a function
that requires any arguments, so we've added a ``wrapper`` function within ``main``
that calls ``get_recent_posts`` with the necessary ``api_key`` arguments, and
we pass this ``wrapper`` function (which needs no arguments) to
:meth:`~workflow.workflow.Workflow.cached_data` instead.

At the top of ``main``, we've added an argument parser using :mod:`argparse`
that can take an optional ``--apikey APIKEY`` argument and an optional ``query``
argument (remember the script doesn't require a query).

Then we check if an API key was passed using ``--apikey``. If it was, we save
it using :attr:`~workflow.workflow.Workflow.settings` (see `below <settings>`).

Once this is done, we post a message to the user informing them that their API
key has been saved and exit the script.

If no API key was specified with ``--apikey``, we try to show/filter Pinboard
posts as before. But first of all, we now have to check to see if we already
have an API key saved. If not, we show the user a warning (No API key set) and
exit the script.

Finally, if we have an API key saved, we retrieve it and show/filter the Pinboard
posts just as before.

Of course, we don't have an API key saved, and we haven't yet set up our Workflow
in Alfred to save one, so the Workflow currently won't work. Try to run it,
and you'll see the warning we just implemented:

.. image:: _static/screen15_no_api_key.png


So let's add that functionality now.


Multi-step actions
------------------

Asking the user for input and saving it is best done in two steps:

1. Ask for the data.
2. Pass it to a second action to save it.

A Script Filter is designed to be called constantly by Alfred and return results.
This time, we just want to get some data, so we'll use a **Keyword** input instead.

Go back to your Workflow in Alfred's Preferences and add a **Keyword** input:

.. image:: _static/screen16_keyword.png

And set it up as follows (we'll use the keyword ``pbsetkey`` because that's what we told the user to use
in the above warning message):

.. image:: _static/screen17_set_apikey_keyword.png

You can now enter ``pbsetkey`` in Alfred and see the following:

.. image:: _static/screen18_pbsetkey.png

It won't do anything yet, though, as we haven't connected its output to anything.

Back in Alfred's Preferences, add a **Run Script** action:

.. image:: _static/screen19_runscript.png

and point it at our ``pinboard.py`` script with the ``--setkey`` argument:

.. image:: _static/screen20_runscript_settings.png

Finally, connect the ``pbsetkey`` **Keyword** to the new **Run Script** action:

.. image:: _static/screen21_connection.png

Now you can call ``pbsetkey`` in Alfred, paste in your Pinboard API key and hit
**ENTER**. It will be saved by the Workflow and ``pbrecent`` will once again
work as expected. Try it.

It's a little confusing receiving no feedback on whether the key was saved or not,
so go back into Alfred's Preferences, and add an **Output > Post Notification**
action to your Workflow:

.. image:: _static/screen22_add_notification.png

In the resulting pop-up, enter a message to be shown in Notification Center:

.. image:: _static/screen22_notification_settings.png

and connect the **Run Script** we just added to it:

.. image:: _static/screen23_three_way.png

Try setting your API key again with ``pbsetkey`` and this time you'll get a
notification that it was saved.

.. _settings:

Saving settings
---------------

Saving the API key was pretty easy (1 line of code). :class:`~workflow.workflow.Settings`
is a special dictionary that automatically saves itself when you change its
contents. It can be used much like a normal dictionary with the caveat that all
values must be serialisable to JSON as the settings are saved as a JSON file in
the Workflow's data directory.

Very simple, yes, but secure? No. A better place to save the API key would be
in the user's Keychain. Let's do that.

Saving settings securely
------------------------

:class:`~workflow.workflow.Workflow` provides three methods for managing data
saved in OS X's Keychain: :meth:`~workflow.workflow.Workflow.get_password`,
:meth:`~workflow.workflow.Workflow.save_password` and :meth:`~workflow.workflow.Workflow.delete_password`.

They are all called with an ``account`` name and an optional ``service`` name
(by default, this is your Workflow's ``bundle ID``).

Change your ``pinboard.py`` script as follows to use Keychain instead of a JSON
file to store your API key:

.. code-block:: python
   :emphasize-lines: 5,58,65-72

    # encoding: utf-8

    import sys
    import argparse
    from workflow import Workflow, ICON_WEB, ICON_WARNING, web, PasswordNotFound


    def get_recent_posts(api_key):
        """Retrieve recent posts from Pinboard.in

        Returns a list of post dictionaries.

        """
        url = 'https://api.pinboard.in/v1/posts/recent'
        params = dict(auth_token=api_key, count=100, format='json')
        r = web.get(url, params)

        # throw an error if request failed
        # Workflow will catch this and show it to the user
        r.raise_for_status()

        # Parse the JSON returned by pinboard and extract the posts
        result = r.json()
        posts = result['posts']
        return posts


    def search_key_for_post(post):
        """Generate a string search key for a post"""
        elements = []
        elements.append(post['description'])  # title of post
        elements.append(post['tags'])  # post tags
        elements.append(post['extended'])  # description
        return u' '.join(elements)


    def main(wf):

        # build argument parser to parse script args and collect their
        # values
        parser = argparse.ArgumentParser()
        # add an optional (nargs='?') --apikey argument and save its
        # value to 'apikey' (dest). This will be called from a separate "Run Script"
        # action with the API key
        parser.add_argument('--setkey', dest='apikey', nargs='?', default=None)
        # add an optional query and save it to 'query'
        parser.add_argument('query', nargs='?', default=None)
        # parse the script's arguments
        args = parser.parse_args(wf.args)

        ####################################################################
        # Save the provided API key
        ####################################################################

        # decide what to do based on arguments
        if args.apikey:  # Script was passed an API key
            # save the key
            wf.save_password('pinboard_api_key', args.apikey)
            return 0  # 0 means script exited cleanly

        ####################################################################
        # Check that we have an API key saved
        ####################################################################

        try:
            api_key = wf.get_password('pinboard_api_key')
        except PasswordNotFound:  # API key has not yet been set
            wf.add_item('No API key set.',
                        'Please use pbsetkey to set your Pinboard API key.',
                        valid=False,
                        icon=ICON_WARNING)
            wf.send_feedback()
            return 0

        ####################################################################
        # View/filter Pinboard posts
        ####################################################################

        query = args.query
        # Retrieve posts from cache if available and no more than 600
        # seconds old

        def wrapper():
            """`cached_data` can only take a bare callable (no args),
            so we need to wrap callables needing arguments in a function
            that needs none.
            """
            return get_recent_posts(api_key)

        posts = wf.cached_data('posts', wrapper, max_age=600)

        # If script was passed a query, use it to filter posts
        if query:
            posts = wf.filter(query, posts, key=search_key_for_post)

        # Loop through the returned posts and add a item for each to
        # the list of results for Alfred
        for post in posts:
            wf.logger.debug(post)
            wf.add_item(title=post['description'],
                        subtitle=post['href'],
                        arg=post['href'],
                        valid=True,
                        icon=ICON_WEB)

        # Send the results to Alfred as XML
        wf.send_feedback()
        return 0


    if __name__ == u"__main__":
        wf = Workflow()
        sys.exit(wf.run(main))

:meth:`~workflow.workflow.Workflow.get_password` raises a
:class:`~workflow.workflow.Workflow.PasswordNotFound` exception if the requested
password isn't in your Keychain, so we import :class:`~workflow.workflow.Workflow.PasswordNotFound`
and change ``if not api_key`` to a ``try ... except`` clause.

Try running your Workflow again. It will complain that you haven't saved your
API key (it's looking in Keychain now, not the settings), so set your API key
once again, and you should be able to browse your recent posts in Alfred once more.

And if you open **Keychain Access**, you'll find the API key safely tucked away
in your Keychain:

.. image:: _static/screen24_keychain.png

As a bonus, if you have multiple Macs and use iCloud Keychain, the API key will
be seamlessly synced across machines, saving you the trouble of setting up the
Workflow multiple times.

"Magic" arguments
-----------------

Now that the API key is stored in Keychain, we don't need it saved in the
Workflow's settings any more (and having it there that kind of defeats the
purpose of using Keychain). To get rid of it, we can use one of **Alfred-Workflow**'s
"magic" arguments: ``workflow:delsettings``.

Open up Alfred, and enter ``pbrecent workflow:delsettings``. You should see the
following message:

.. image:: _static/screen25_magic.png

**Alfred-Workflow** has recognised one of its "magic" arguments, performed the
appropriate action, posted a notification and exited the Workflow.

Currently, the following magic arguments are available:

- ``workflow:delsettings`` — deletes the Workflow's settings file
- ``workflow:delcache`` — clears the Workflow's cache
- ``workflow:openlog`` — open the Workflow's log file in the default application (usually **Console.app**)

These are to aid coders in the development and debugging of Workflows. In particular,
it makes debugging errors encountered by Terminal-averse users much easier: any
exceptions raised within the :meth:`~workflow.workflow.Workflow.run` method are
logged together with the corresponding traceback, and you can ask users to call
your Workflow's keyword with the ``workflow:openlog`` query to more easily send
you the contents of the log.

**Note:** magic arguments will only work with scripts that accept arguments *and*
use the :attr:`~workflow.workflow.Workflow.args` property (where "magic" arguments
are parsed).

You can turn off magic arguments by passing ``capture_args=False`` to
:class:`~workflow.workflow.Workflow` on instantiation, or call the corresponding
:meth:`~workflow.workflow.Workflow.open_log`, :meth:`~workflow.workflow.Workflow.clear_cache`
and :meth:`~workflow.workflow.Workflow.clear_settings` methods directly, perhaps
assigning them to your own Keywords.

Logging
-------

There's a log, you say? Yup. There's a :class:`logging.Logger`
instance at :attr:`Workflow.logger <workflow.workflow.Workflow.logger>` configured to output to
both the Terminal and your Workflow's log file. Normally, I use it like this:

.. code-block:: python

    from workflow import Workflow

    log = None


    def main(wf):
        log.debug('Started')

    if __name__ == '__main__':
        wf = Workflow()
        log = wf.logger
        wf.run(main)

Assigning :attr:`~workflow.workflow.Workflow.logger` to the module-global ``log``
means it can be accessed from within any function without having to pass the
:class:`~workflow.workflow.Workflow` or :attr:`~workflow.workflow.Workflow.logger`
instance around.

Spit and polish
---------------

So far, the Workflow's looking pretty good. But there are still a couple of things
that could be better. For one, it's not necessarily obvious to a user where to
find their Pinboard API key (it took me a good, hard Googling to find it while
writing these tutorials). For another, the Workflow is unresponsive while updating
the list of recent posts from Pinboard. That can't be helped if we don't have any
posts cached, but apart from the very first run, we always will, so why don't
we show what we have and update in the background?

Let's fix those issues. The easy one first.

Two actions, one keyword
^^^^^^^^^^^^^^^^^^^^^^^^

To solve the first issue (Pinboard API keys being hard to find), we'll add a second
**Keyword** input that responds to the same ``pbsetkey`` keyword as our other
action, but this one will just send the user to the Pinboard
`password settings page <https://pinboard.in/settings/password>`_ where the API
keys are kept.

Go back to your Workflow in Alfred's Preferences and add a new **Keyword** with
the following settings:

.. image:: _static/screen26_keyword2.png

Now when you type ``pbsetkey`` into Alfred, you should see two options:

.. image:: _static/screen27_1_keyword_2_actions.png

The second action doesn't do anything yet, of course, because we haven't connected
it to anything. So add an **Open URL** action in Alfred, enter this URL:

https://pinboard.in/settings/password

and leave all the settings at their defaults.

.. image:: _static/screen28_open_url.png

Finally, connect your new **Keyword** to the new **Open URL** action:

.. image:: _static/screen29_link.png

Enter ``pbsetkey`` into Alfred once more and try out the new action. Pinboard
should open in your default browser.

Easy peasy.

Our last hurrah
^^^^^^^^^^^^^^^

All that remains is for our Workflow to provide the blazing fast results Alfred
users have come to expect. No waiting around for glacial web services for the
likes of us. As long as we have some posts saved in the cache, we can show those
while grabbing an updated list in the background (and notifying the user of
the update, of course).

Now, there are different ways to start a background process. We could ask the user
to set up a `cron` job, but `cron` isn't the easiest software to use. We could
add and load a Launch Agent, but that'd run indefinitely, whether or not the
Workflow is being used, and even if the Workflow were uninstalled. So we'd
best start our background process from within the Workflow itself.

Normally, you'd use :class:`subprocess.Popen` to start a background process, but
that doesn't work quite as you'd expect in Alfred: it treats your Workflow
as still running till the background process has finished, too, so it won't call
your Workflow with a new query till the Pinboard update is done. Which is
exactly what happens now.

To solve this problem, we're still going to use :class:`subprocess.Popen`, but
our updater script is going to fork into the background and become a daemon process
before performing the update. This way, it will appear to exit immediately, so
Alfred will keep on calling our Workflow every time the query changes.

Meanwhile, our main Workflow script will check if the background updater is
running and post a useful, friendly notification if it is.

Let's have at it.

