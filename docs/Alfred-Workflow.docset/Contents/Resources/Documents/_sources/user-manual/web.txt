
.. _web-data:

============================
Retrieving data from the web
============================

The `unit tests`_ in the source repository contain examples of pretty
much everything :mod:`workflow.web` can do:

* `GET`_ and `POST`_ variables
* `Retrieve and decode JSON`_
* `Post JSON`_
* `Post forms`_
* Automatically handle encoding for `HTML`_ and `XML`_
* `Basic authentication`_
* File uploads `with forms`_ and `without forms`_
* `Download large files`_
* `Variable timeouts`_
* `Ignore redirects`_

See the :ref:`API documentation <web>` for more information.

.. _GET: https://github.com/deanishe/alfred-workflow/blob/fdc7c001c2cb76a41aee3e5a755486a977a36b20/tests/test_web.py#L128
.. _POST: https://github.com/deanishe/alfred-workflow/blob/fdc7c001c2cb76a41aee3e5a755486a977a36b20/tests/test_web.py#L76
.. _unit tests: https://github.com/deanishe/alfred-workflow/blob/fdc7c001c2cb76a41aee3e5a755486a977a36b20/tests/test_web.py
.. _Ignore redirects: https://github.com/deanishe/alfred-workflow/blob/fdc7c001c2cb76a41aee3e5a755486a977a36b20/tests/test_web.py#L67
.. _Variable timeouts: https://github.com/deanishe/alfred-workflow/blob/fdc7c001c2cb76a41aee3e5a755486a977a36b20/tests/test_web.py#L101
.. _Post forms: https://github.com/deanishe/alfred-workflow/blob/fdc7c001c2cb76a41aee3e5a755486a977a36b20/tests/test_web.py#L76
.. _Post JSON: https://github.com/deanishe/alfred-workflow/blob/fdc7c001c2cb76a41aee3e5a755486a977a36b20/tests/test_web.py#L86
.. _HTML: https://github.com/deanishe/alfred-workflow/blob/fdc7c001c2cb76a41aee3e5a755486a977a36b20/tests/test_web.py#L106
.. _XML: https://github.com/deanishe/alfred-workflow/blob/fdc7c001c2cb76a41aee3e5a755486a977a36b20/tests/test_web.py#L121
.. _Basic authentication: https://github.com/deanishe/alfred-workflow/blob/fdc7c001c2cb76a41aee3e5a755486a977a36b20/tests/test_web.py#L137
.. _with forms: https://github.com/deanishe/alfred-workflow/blob/fdc7c001c2cb76a41aee3e5a755486a977a36b20/tests/test_web.py#L153
.. _without forms: https://github.com/deanishe/alfred-workflow/blob/fdc7c001c2cb76a41aee3e5a755486a977a36b20/tests/test_web.py#L173
.. _Retrieve and decode JSON: https://github.com/deanishe/alfred-workflow/blob/fdc7c001c2cb76a41aee3e5a755486a977a36b20/tests/test_web.py#L189
.. _Download large files: https://github.com/deanishe/alfred-workflow/blob/fdc7c001c2cb76a41aee3e5a755486a977a36b20/tests/test_web.py#L197
