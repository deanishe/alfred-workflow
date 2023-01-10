# encoding: utf-8
#
# Copyright (c) 2014 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-02-15
#

"""
Basic, ``requests``-like API for retrieving data from the Web.

Intended to replace basic functionality of ``requests``, but at
1/200th of the size.

Features:

- JSON requests and responses
- Form data submission
- File uploads
- Redirection support

**WARNING**: As ``web.py`` is based on Python 2's standard HTTP libraries, it
**does not** verify SSL certificates when establishing HTTPS connections.

As a result, you *must not* use this module for sensitive connections.

If you require certificate verification (which you really should), you should
use the `requests <http://docs.python-requests.org/en/latest/>`_
Python library (upon which the `web.py` API is based) or the
command-line tool `cURL <http://curl.haxx.se/>`_ instead.

"""

from __future__ import print_function

import codecs
import json
import mimetypes
import random
import re
import socket
import string
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from builtins import object, range, str
from http.client import HTTPMessage, HTTPResponse

USER_AGENT = "alfred-workflow-0.1"

# Valid characters for multipart form data boundaries
BOUNDARY_CHARS = string.digits + string.ascii_letters

# Table mapping response codes to messages; entries have the
# form {code: message}.
RESPONSES = {
    100: "Continue",
    101: "Switching Protocols",
    200: "OK",
    201: "Created",
    202: "Accepted",
    203: "Non-Authoritative Information",
    204: "No Content",
    205: "Reset Content",
    206: "Partial Content",
    300: "Multiple Choices",
    301: "Moved Permanently",
    302: "Found",
    303: "See Other",
    304: "Not Modified",
    305: "Use Proxy",
    307: "Temporary Redirect",
    400: "Bad Request",
    401: "Unauthorized",
    402: "Payment Required",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    406: "Not Acceptable",
    407: "Proxy Authentication Required",
    408: "Request Timeout",
    409: "Conflict",
    410: "Gone",
    411: "Length Required",
    412: "Precondition Failed",
    413: "Request Entity Too Large",
    414: "Request-URI Too Long",
    415: "Unsupported Media Type",
    416: "Requested Range Not Satisfiable",
    417: "Expectation Failed",
    500: "Internal Server Error",
    501: "Not Implemented",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
    505: "HTTP Version Not Supported",
}


def str_dict(dic):
    """Convert keys and values in ``dic`` into UTF-8-encoded :class:`str`

    :param dic: :class:`dict` of Unicode strings
    :returns: :class:`dict`

    """
    dic2 = {}
    for k, v in list(dic.items()):
        if isinstance(k, str):
            k = k.encode("utf-8")
        if isinstance(v, str):
            v = v.encode("utf-8")
        dic2[k] = v
    return dic2


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Prevent redirections"""

    def redirect_request(self, req, fp, code, msg, hdrs, newurl):
        return None


class Response(object):
    """
    Returned by :func:`request` / :func:`get` / :func:`post` functions.

    A simplified version of the ``Response`` object in the ``requests`` library.

    >>> r = request('http://www.google.com')
    >>> r.status_code
    200
    >>> r.encoding
    ISO-8859-1
    >>> r.content  # bytes
    <html> ...
    >>> r.text  # unicode, decoded according to charset in HTTP header/meta tag
    u'<html> ...'
    >>> r.json()  # content parsed as JSON

    """

    def __init__(self, request):
        """Call `request` with :mod:`urllib2` and process results.

        :param request: :class:`urllib2.Request` instance

        """

        self.request = request
        self.url = None
        self.raw: HTTPResponse | None = None
        self._encoding = None
        self.error = None
        self.status_code = None
        self.reason = None
        self.headers: dict = {}
        self._content: bytes | None = None

        # Execute query
        try:
            self.raw = urllib.request.urlopen(request)
        except urllib.error.HTTPError as err:
            self.error = err
            try:
                self.url = err.geturl()
            # sometimes (e.g. when authentication fails)
            # urllib can't get a URL from an HTTPError
            except AttributeError:
                pass
            self.status_code = err.code
        else:
            self.status_code = self.raw.getcode()
            self.url = self.raw.geturl()
        self.reason = RESPONSES.get(self.status_code)

        # Parse additional info if request succeeded
        if not self.error:
            headers: HTTPMessage = self.raw.headers
            self.transfer_encoding = 'utf-8'
            self.mimetype = headers.get_content_type()
            for key in list(headers.keys()):
                self.headers[key.lower()] = headers.get(key)

    def json(self):
        """Decode response contents as JSON.

        :returns: decoded JSON
        :rtype: ``list`` / ``dict``

        """

        return json.loads(self.content, self.encoding or "utf-8")

    @property
    def encoding(self) -> str | None:
        """Return text encoding of document or ``None``

        :returns: ``str``

        """

        if not self._encoding:
            self._encoding = self._get_encoding()

        return self._encoding

    @property
    def content(self) -> bytes:
        """Return raw content of response (i.e. bytes)

        :returns: ``str``

        """

        if not self._content:
            self._content = self.raw.read()

        return self._content

    @property
    def text(self) -> str:
        """Return unicode-decoded content of response.

        :returns: ``unicode``

        """

        if self.encoding:
            return unicodedata.normalize("NFC", str(self.content, self.encoding))
        return self.content

    def iter_content(self, chunk_size=1, decode_unicode=False):
        """Iterate over response data.

        .. versionadded:: 1.6

        :param chunk_size: Number of bytes to read into memory
        :type chunk_size: ``int``
        :param decode_unicode: Decode to Unicode using detected encoding
        :type decode_unicode: ``Boolean``
        :returns: iterator

        """

        def decode_stream(iterator, r):

            decoder = codecs.getincrementaldecoder(r.encoding)(errors="replace")

            for chunk in iterator:
                rv = decoder.decode(chunk)
                if rv:
                    yield rv
            rv = decoder.decode(b"", final=True)
            if rv:
                yield rv  # pragma: nocover

        def generate():
            while True:
                chunk = self.raw.read(chunk_size)
                if not chunk:
                    break
                yield chunk

        chunks = generate()

        if decode_unicode and self.encoding:
            chunks = decode_stream(chunks, self)

        return chunks

    def raise_for_status(self):
        """Raise stored error if one occurred.

        error will be instance of :class:`urllib2.HTTPError`
        """

        if self.error:
            raise self.error
        return

    def _get_encoding(self) -> str | None:
        """Get encoding from HTTP headers or content.

        :returns: encoding or `None`
        :rtype: ``unicode`` or ``None``

        """

        headers = self.raw.info()
        encoding = None

        if headers.get_param("charset"):
            encoding = headers.get_param("charset")

        # HTTP Content-Type header
        for k, v in headers.get_params():
            if k == "charset":
                encoding = v
                break

        # Encoding declared in document should override HTTP headers
        if self.mimetype == "text/html":  # sniff HTML headers
            m = re.search("""<meta.+charset=["']{0,1}(.+?)["'].*>""", str(self.content))
            if m:
                encoding = m.group(1)

        elif (
            self.mimetype.startswith("application/")
            or self.mimetype.startswith("text/")
        ) and "xml" in self.mimetype:
            m = re.search("""<?xml.+encoding=["'](.+?)["'][^>]*\?>""", str(self.content))
            if m:
                encoding = m.group(1)

        # Format defaults
        if self.mimetype == "application/json" and not encoding:
            # The default encoding for JSON
            encoding = "utf-8"

        elif self.mimetype == "application/xml" and not encoding:
            # The default for 'application/xml'
            encoding = "utf-8"

        if encoding:
            encoding = encoding.lower()

        return encoding


def request(
    method: str,
    url: str,
    params: dict | None = None,
    data: dict | None = None,
    headers: dict | None = None,
    cookies: dict | None = None,
    files=None,
    auth: tuple | None = None,
    timeout: int = 60,
    allow_redirects: bool = False,
) -> Response:
    """Initiate an HTTP(S) request. Returns :class:`Response` object.

    :param method: 'GET' or 'POST'
    :type method: ``unicode``
    :param url: URL to open
    :type url: ``unicode``
    :param params: mapping of URL parameters
    :type params: ``dict``
    :param data: mapping of form data ``{'field_name': 'value'}`` or ``str``
    :type data: ``dict`` or ``str``
    :param headers: HTTP headers
    :type headers: ``dict``
    :param cookies: cookies to send to server
    :type cookies: ``dict``
    :param files: files to upload
    :type files:
    :param auth: username, password
    :type auth: ``tuple``
    :param timeout: connection timeout limit in seconds
    :type timeout: ``int``
    :param allow_redirects: follow redirections
    :type allow_redirects: ``Boolean``
    :returns: :class:`Response` object

    """

    socket.setdefaulttimeout(timeout)

    # Default handlers
    openers = []

    if not allow_redirects:
        openers.append(NoRedirectHandler())

    if auth:  # Add authorisation handler
        username, password = auth
        password_manager = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        password_manager.add_password(None, url, username, password)
        auth_manager = urllib.request.HTTPBasicAuthHandler(password_manager)
        openers.append(auth_manager)

    # Install our custom chain of openers
    opener = urllib.request.build_opener(*openers)
    urllib.request.install_opener(opener)

    if not headers:
        headers = {}
    if "User-Agent" not in headers:
        headers["User-Agent"] = USER_AGENT

    if files:
        if not data:
            data = {}
        new_headers, data = encode_multipart_formdata(data, files)
        headers.update(new_headers)
    elif data and isinstance(data, dict):
        data = urllib.parse.urlencode(str_dict(data))

    # Make sure everything is encoded text
    headers = str_dict(headers)

    if params:  # GET args (POST args are handled in encode_multipart_formdata)
        url = url + "?" + urllib.parse.urlencode(str_dict(params))

    req = urllib.request.Request(url, data, headers)
    return Response(req)


def get(
    url: str,
    params=None,
    headers=None,
    cookies=None,
    auth=None,
    timeout=60,
    allow_redirects=True,
) -> Response:
    """Initiate a GET request. Arguments as for :func:`request` function.

    :returns: :class:`Response` instance

    """

    return request(
        "GET",
        url,
        params,
        headers=headers,
        cookies=cookies,
        auth=auth,
        timeout=timeout,
        allow_redirects=allow_redirects,
    )


def post(
    url,
    params=None,
    data=None,
    headers=None,
    cookies=None,
    files=None,
    auth=None,
    timeout=60,
    allow_redirects=False,
):
    """Initiate a POST request. Arguments as for :func:`request` function.

    :returns: :class:`Response` instance

    """
    return request(
        "POST",
        url,
        params,
        data,
        headers,
        cookies,
        files,
        auth,
        timeout,
        allow_redirects,
    )


def encode_multipart_formdata(fields, files):
    """Encode form data (``fields``) and ``files`` for POST request.

    :param fields: mapping of ``{name : value}`` pairs for normal form fields.
    :type fields: :class:`dict`
    :param files: dictionary of fieldnames/files elements for file data.
                  See below for details.
    :type files: :class:`dict` of :class:`dicts`
    :returns: ``(headers, body)`` ``headers`` is a :class:`dict` of HTTP headers
    :rtype: 2-tuple ``(dict, str)``

    The ``files`` argument is a dictionary::

        {'fieldname' : { 'filename': 'blah.txt',
                         'content': '<binary data>',
                         'mimetype': 'text/plain'}
        }

    - ``fieldname`` is the name of the field in the HTML form.
    - ``mimetype`` is optional. If not provided, :mod:`mimetypes` will be used to guess the mimetype, or ``application/octet-stream`` will be used.

    """

    def get_content_type(filename):
        """Return or guess mimetype of ``filename``.

        :param filename: filename of file
        :type filename: unicode/string
        :returns: mime-type, e.g. ``text/html``
        :rtype: :class:``str``

        """

        return mimetypes.guess_type(filename)[0] or "application/octet-stream"

    boundary = "-----" + "".join(random.choice(BOUNDARY_CHARS) for i in range(30))
    CRLF = "\r\n"
    output = []

    # Normal form fields
    for (name, value) in list(fields.items()):
        if isinstance(name, str):
            name = name.encode("utf-8")
        if isinstance(value, str):
            value = value.encode("utf-8")
        output.append("--" + boundary)
        output.append('Content-Disposition: form-data; name="%s"' % name)
        output.append("")
        output.append(value)

    # Files to upload
    for name, d in list(files.items()):
        filename = d["filename"]
        content = d["content"]
        if "mimetype" in d:
            mimetype = d["mimetype"]
        else:
            mimetype = get_content_type(filename)
        if isinstance(name, str):
            name = name.encode("utf-8")
        if isinstance(filename, str):
            filename = filename.encode("utf-8")
        if isinstance(mimetype, str):
            mimetype = mimetype.encode("utf-8")
        output.append("--" + boundary)
        output.append(
            "Content-Disposition: form-data; "
            'name="%s"; filename="%s"' % (name, filename)
        )
        output.append("Content-Type: %s" % mimetype)
        output.append("")
        output.append(content)

    output.append("--" + boundary + "--")
    output.append("")
    body = CRLF.join(output)
    headers = {
        "Content-Type": "multipart/form-data; boundary=%s" % boundary,
        "Content-Length": str(len(body)),
    }
    return (headers, body)
