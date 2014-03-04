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

So now we're going to edit the Workflow so users can add their API key from the
comfort of Alfred's friendly query box.


Performing multiple actions from one script
-------------------------------------------

To set the user's API key, we're going to need a new action. We could write a
second script to do this, but we're going to stick with one script and make it
smart enough to do two things, instead. The advantage of using one script is
that if you build a workflow with lots of actions, you don't have a dozen or more
scripts to manage.




Saving settings
---------------

Saving settings securely
------------------------

Multi-step actions
------------------

