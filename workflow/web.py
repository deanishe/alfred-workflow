# encoding: utf-8
#
# Copyright (c) 2014 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-02-15
#

"""Lightweight HTTP library with a requests-like interface."""



import codecs
import json
import mimetypes
import os
import random
import re
import socket
import string
import unicodedata
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import urllib.parse
import zlib

__version__ = open(os.path.join(os.path.dirname(__file__), 'version')).read()

USER_AGENT = ('Alfred-Workflow/' + __version__ +
              ' (+http://www.deanishe.net/alfred-workflow)')

# Valid characters for multipart form data boundaries
BOUNDARY_CHARS = string.digits + string.ascii_letters

# HTTP response codes
RESPONSES = {
    100: 'Continue',
    101: 'Switching Protocols',
    200: 'OK',
    201: 'Created',
    202: 'Accepted',
    203: 'Non-Authoritative Information',
    204: 'No Content',
    205: 'Reset Content',
    206: 'Partial Content',
    300: 'Multiple Choices',
    301: 'Moved Permanently',
    302: 'Found',
    303: 'See Other',
    304: 'Not Modified',
    305: 'Use Proxy',
    307: 'Temporary Redirect',
    400: 'Bad Request',
    401: 'Unauthorized',
    402: 'Payment Required',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    406: 'Not Acceptable',
    407: 'Proxy Authentication Required',
    408: 'Request Timeout',
    409: 'Conflict',
    410: 'Gone',
    411: 'Length Required',
    412: 'Precondition Failed',
    413: 'Request Entity Too Large',
    414: 'Request-URI Too Long',
    415: 'Unsupported Media Type',
    416: 'Requested Range Not Satisfiable',
    417: 'Expectation Failed',
    500: 'Internal Server Error',
    501: 'Not Implemented',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
    504: 'Gateway Timeout',
    505: 'HTTP Version Not Supported'
}


def str_dict(dic):
    """Convert keys and values in ``dic`` into UTF-8-encoded :class:`str`.

    :param dic: Mapping of Unicode strings
    :type dic: dict
    :returns: Dictionary containing only UTF-8 strings
    :rtype: dict

    """
    if isinstance(dic, CaseInsensitiveDictionary):
        dic2 = CaseInsensitiveDictionary()
    else:
        dic2 = {}
    for k, v in list(dic.items()):
        if isinstance(k, str):
            k = k.encode('utf-8')
        if isinstance(v, str):
            v = v.encode('utf-8')
        dic2[k] = v
    return dic2


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Prevent redirections."""

    def redirect_request(self, *args):
        """Ignore redirect."""
        return None


# Adapted from https://gist.github.com/babakness/3901174
class CaseInsensitiveDictionary(dict):
    """Dictionary with caseless key search.

    Enables case insensitive searching while preserving case sensitivity
    when keys are listed, ie, via keys() or items() methods.

    Works by storing a lowercase version of the key as the new key and
    stores the original key-value pair as the key's value
    (values become dictionaries).

    """

    def __init__(self, initval=None):
        """Create new case-insensitive dictionary."""
        if isinstance(initval, dict):
            for key, value in initval.items():
                self.__setitem__(key, value)

        elif isinstance(initval, list):
            for (key, value) in initval:
                self.__setitem__(key, value)

    def __contains__(self, key):
        return dict.__contains__(self, key.lower())

    def __getitem__(self, key):
        return dict.__getitem__(self, key.lower())['val']

    def __setitem__(self, key, value):
        return dict.__setitem__(self, key.lower(), {'key': key, 'val': value})

    def get(self, key, default=None):
        """Return value for case-insensitive key or default."""
        try:
            v = dict.__getitem__(self, key.lower())
        except KeyError:
            return default
        else:
            return v['val']

    def update(self, other):
        """Update values from other ``dict``."""
        for k, v in list(other.items()):
            self[k] = v

    def items(self):
        """Return ``(key, value)`` pairs."""
        return [(v['key'], v['val']) for v in dict.values(self)]

    def keys(self):
        """Return original keys."""
        return [v['key'] for v in dict.values(self)]

    def values(self):
        """Return all values."""
        return [v['val'] for v in dict.values(self)]


class Request(urllib.request.Request):
    """Subclass of :class:`urllib.Request` that supports custom methods."""

    def __init__(self, *args, **kwargs):
        """Create a new :class:`Request`."""
        self._method = kwargs.pop('method', None)
        urllib.request.Request.__init__(self, *args, **kwargs)

    def get_method(self):
        return self._method.upper()


class Response(object):
    """
    Returned by :func:`request` / :func:`get` / :func:`post` functions.

    Simplified version of the ``Response`` object in the ``requests`` library.

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

    def __init__(self, request, stream=False):
        """Call `request` with :mod:`urllib` and process results.

        :param request: :class:`Request` instance
        :param stream: Whether to stream response or retrieve it all at once
        :type stream: bool

        """
        self.request = request
        self._stream = stream
        self.url = None
        self.raw = None
        self._encoding = None
        self.error = None
        self.status_code = None
        self.reason = None
        self.headers = CaseInsensitiveDictionary()
        self._content = None
        self._content_loaded = False
        self._gzipped = False

        # Execute query
        try:
            self.raw = urllib.request.urlopen(request)
        except urllib.error.HTTPError as err:
            self.error = err
            try:
                self.url = err.geturl()
            # sometimes (e.g. when authentication fails)
            # urllib can't get a URL from an HTTPError
            # This behaviour changes across Python versions,
            # so no test cover (it isn't important).
            except AttributeError:  # pragma: no cover
                pass
            self.status_code = err.code
        else:
            self.status_code = self.raw.getcode()
            self.url = self.raw.geturl()
        self.reason = RESPONSES.get(self.status_code)

        # Parse additional info if request succeeded
        if not self.error:
            headers = self.raw.info()
            self.transfer_encoding = headers.get_content_charset()
            self.mimetype = headers.get_content_type()
            for key in list(headers.keys()):
                self.headers[key.lower()] = headers.get(key)

            # Is content gzipped?
            # Transfer-Encoding appears to not be used in the wild
            # (contrary to the HTTP standard), but no harm in testing
            # for it
            if 'gzip' in headers.get('content-encoding', '') or \
                    'gzip' in headers.get('transfer-encoding', ''):
                self._gzipped = True

    @property
    def stream(self):
        """Whether response is streamed.

        Returns:
            bool: `True` if response is streamed.

        """
        return self._stream

    @stream.setter
    def stream(self, value):
        if self._content_loaded:
            raise RuntimeError("`content` has already been read from "
                               "this Response.")

        self._stream = value

    def json(self):
        """Decode response contents as JSON.

        :returns: object decoded from JSON
        :rtype: list, dict or unicode

        """
        return json.loads(self.content)

    @property
    def encoding(self):
        """Text encoding of document or ``None``.

        :returns: Text encoding if found.
        :rtype: str or ``None``

        """
        if not self._encoding:
            self._encoding = self._get_encoding()

        return self._encoding

    @property
    def content(self):
        """Raw content of response (i.e. bytes).

        :returns: Body of HTTP response
        :rtype: str

        """
        if not self._content:

            # Decompress gzipped content
            if self._gzipped:
                decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
                self._content = decoder.decompress(self.raw.read())

            else:
                self._content = self.raw.read()

            self._content_loaded = True

        return self._content

    @property
    def text(self):
        """Unicode-decoded content of response body.

        If no encoding can be determined from HTTP headers or the content
        itself, the encoded response body will be returned instead.

        :returns: Body of HTTP response
        :rtype: unicode or str

        """
        if self.encoding:
            return unicodedata.normalize(
                'NFC', str(self.content, self.encoding)
            )
        return self.content

    def iter_content(self, chunk_size=4096, decode_unicode=False):
        """Iterate over response data.

        .. versionadded:: 1.6

        :param chunk_size: Number of bytes to read into memory
        :type chunk_size: int
        :param decode_unicode: Decode to Unicode using detected encoding
        :type decode_unicode: bool
        :returns: iterator

        """
        if not self.stream:
            raise RuntimeError("You cannot call `iter_content` on a "
                               "Response unless you passed `stream=True`"
                               " to `get()`/`post()`/`request()`.")

        if self._content_loaded:
            raise RuntimeError(
                "`content` has already been read from this Response.")

        def decode_stream(iterator, r):
            dec = codecs.getincrementaldecoder(r.encoding)(errors='replace')

            for chunk in iterator:
                data = dec.decode(chunk)
                if data:
                    yield data

            data = dec.decode(b'', final=True)
            if data:  # pragma: no cover
                yield data

        def generate():
            if self._gzipped:
                decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)

            while True:
                chunk = self.raw.read(chunk_size)
                if not chunk:
                    break

                if self._gzipped:
                    chunk = decoder.decompress(chunk)

                yield chunk

        chunks = generate()

        if decode_unicode and self.encoding:
            chunks = decode_stream(chunks, self)

        return chunks

    def save_to_path(self, filepath):
        """Save retrieved data to file at ``filepath``.

        .. versionadded: 1.9.6

        :param filepath: Path to save retrieved data.

        """
        filepath = os.path.abspath(filepath)
        dirname = os.path.dirname(filepath)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        self.stream = True

        with open(filepath, 'wb') as fileobj:
            for data in self.iter_content():
                fileobj.write(data)

    def raise_for_status(self):
        """Raise stored error if one occurred.

        error will be instance of :class:`urllib.HTTPError`
        """
        if self.error is not None:
            raise self.error
        return

    def _get_encoding(self):
        """Get encoding from HTTP headers or content.

        :returns: encoding or `None`
        :rtype: unicode or ``None``

        """
        headers = self.raw.info()
        encoding = None

        if headers.get_content_charset():
            encoding = headers.get_content_charset()

        # HTTP Content-Type header
        for param, value in (headers.get_params() or []):
            if param.startswith('charset'):
                encoding = value
                break

        if not self.stream:  # Try sniffing response content
            # Encoding declared in document should override HTTP headers
            if self.mimetype == 'text/html':  # sniff HTML headers
                m = re.search(br"""<meta.+charset=["']{0,1}(.+?)["'].*>""",
                              self.content)
                if m:
                    encoding = m.group(1).decode('utf8')

            elif ((self.mimetype.startswith('application/')
                   or self.mimetype.startswith('text/'))
                  and 'xml' in self.mimetype):
                m = re.search(br"""<?xml.+encoding=["'](.+?)["'][^>]*\?>""",
                              self.content)
                if m:
                    encoding = m.group(1).decode('utf8')

        # Format defaults
        if self.mimetype == 'application/json' and not encoding:
            # The default encoding for JSON
            encoding = 'utf-8'

        elif self.mimetype == 'application/xml' and not encoding:
            # The default for 'application/xml'
            encoding = 'utf-8'

        if encoding:
            encoding = encoding.lower()

        return encoding


def request(method, url, params=None, data=None, headers=None, cookies=None,
            files=None, auth=None, timeout=60, allow_redirects=False,
            stream=False):
    """Initiate an HTTP(S) request. Returns :class:`Response` object.

    :param method: 'GET' or 'POST'
    :type method: unicode
    :param url: URL to open
    :type url: unicode
    :param params: mapping of URL parameters
    :type params: dict
    :param data: mapping of form data ``{'field_name': 'value'}`` or
        :class:`str`
    :type data: dict or str
    :param headers: HTTP headers
    :type headers: dict
    :param cookies: cookies to send to server
    :type cookies: dict
    :param files: files to upload (see below).
    :type files: dict
    :param auth: username, password
    :type auth: tuple
    :param timeout: connection timeout limit in seconds
    :type timeout: int
    :param allow_redirects: follow redirections
    :type allow_redirects: bool
    :param stream: Stream content instead of fetching it all at once.
    :type stream: bool
    :returns: Response object
    :rtype: :class:`Response`


    The ``files`` argument is a dictionary::

        {'fieldname' : { 'filename': 'blah.txt',
                         'content': '<binary data>',
                         'mimetype': 'text/plain'}
        }

    * ``fieldname`` is the name of the field in the HTML form.
    * ``mimetype`` is optional. If not provided, :mod:`mimetypes` will
      be used to guess the mimetype, or ``application/octet-stream``
      will be used.

    """
    # TODO: cookies
    socket.setdefaulttimeout(timeout)

    # Default handlers
    openers = [urllib.request.ProxyHandler(urllib.request.getproxies())]

    if not allow_redirects:
        openers.append(NoRedirectHandler())

    if auth is not None:  # Add authorisation handler
        username, password = auth
        password_manager = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        password_manager.add_password(None, url, username, password)
        auth_manager = urllib.request.HTTPBasicAuthHandler(password_manager)
        openers.append(auth_manager)

    # Install our custom chain of openers
    opener = urllib.request.build_opener(*openers)
    urllib.request.install_opener(opener)

    if not headers:
        headers = CaseInsensitiveDictionary()
    else:
        headers = CaseInsensitiveDictionary(headers)

    if 'user-agent' not in headers:
        headers['user-agent'] = USER_AGENT

    # Accept gzip-encoded content
    encodings = [s.strip() for s in
                 headers.get('accept-encoding', '').split(',')
                 if s.strip()]
    if 'gzip' not in encodings:
        encodings.append('gzip')

    headers['accept-encoding'] = ', '.join(encodings)

    if files:
        if not data:
            data = {}
        new_headers, data = encode_multipart_formdata(data, files)
        headers.update(new_headers)
    elif data and isinstance(data, dict):
        data = urllib.parse.urlencode(str_dict(data))

    # Make sure everything is encoded text
    headers = str_dict(headers)

    if isinstance(data, str):
        data = data.encode('utf-8')

    if params:  # GET args (POST args are handled in encode_multipart_formdata)

        scheme, netloc, path, query, fragment = urllib.parse.urlsplit(url)

        if query:  # Combine query string and `params`
            url_params = urllib.parse.parse_qs(query)
            # `params` take precedence over URL query string
            url_params.update(params)
            params = url_params

        query = urllib.parse.urlencode(str_dict(params), doseq=True)
        url = urllib.parse.urlunsplit((scheme, netloc, path, query, fragment))

    req = Request(url, data, headers, method=method)
    return Response(req, stream)


def get(url, params=None, headers=None, cookies=None, auth=None,
        timeout=60, allow_redirects=True, stream=False):
    """Initiate a GET request. Arguments as for :func:`request`.

    :returns: :class:`Response` instance

    """
    return request('GET', url, params, headers=headers, cookies=cookies,
                   auth=auth, timeout=timeout, allow_redirects=allow_redirects,
                   stream=stream)


def delete(url, params=None, data=None, headers=None, cookies=None, auth=None,
           timeout=60, allow_redirects=True, stream=False):
    """Initiate a DELETE request. Arguments as for :func:`request`.

    :returns: :class:`Response` instance

    """
    return request('DELETE', url, params, data, headers=headers,
                   cookies=cookies, auth=auth, timeout=timeout,
                   allow_redirects=allow_redirects, stream=stream)


def post(url, params=None, data=None, headers=None, cookies=None, files=None,
         auth=None, timeout=60, allow_redirects=False, stream=False):
    """Initiate a POST request. Arguments as for :func:`request`.

    :returns: :class:`Response` instance

    """
    return request('POST', url, params, data, headers, cookies, files, auth,
                   timeout, allow_redirects, stream)


def put(url, params=None, data=None, headers=None, cookies=None, files=None,
        auth=None, timeout=60, allow_redirects=False, stream=False):
    """Initiate a PUT request. Arguments as for :func:`request`.

    :returns: :class:`Response` instance

    """
    return request('PUT', url, params, data, headers, cookies, files, auth,
                   timeout, allow_redirects, stream)


def encode_multipart_formdata(fields, files):
    """Encode form data (``fields``) and ``files`` for POST request.

    :param fields: mapping of ``{name : value}`` pairs for normal form fields.
    :type fields: dict
    :param files: dictionary of fieldnames/files elements for file data.
                  See below for details.
    :type files: dict of :class:`dict`
    :returns: ``(headers, body)`` ``headers`` is a
        :class:`dict` of HTTP headers
    :rtype: 2-tuple ``(dict, str)``

    The ``files`` argument is a dictionary::

        {'fieldname' : { 'filename': 'blah.txt',
                         'content': '<binary data>',
                         'mimetype': 'text/plain'}
        }

    - ``fieldname`` is the name of the field in the HTML form.
    - ``mimetype`` is optional. If not provided, :mod:`mimetypes` will
      be used to guess the mimetype, or ``application/octet-stream``
      will be used.

    """
    def get_content_type(filename):
        """Return or guess mimetype of ``filename``.

        :param filename: filename of file
        :type filename: unicode/str
        :returns: mime-type, e.g. ``text/html``
        :rtype: str

        """
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

    boundary = b'-----' + b''.join(
        random.choice(BOUNDARY_CHARS).encode('ascii') for i in range(30)
    )
    CRLF = b'\r\n'
    output = []

    # Normal form fields
    for (name, value) in list(fields.items()):
        if isinstance(name, str):
            name = name.encode('utf-8')
        if isinstance(value, str):
            value = value.encode('utf-8')
        output.append(b'--' + boundary)
        output.append(b'Content-Disposition: form-data; name="%b"' % name)
        output.append(b'')
        output.append(value)

    # Files to upload
    for name, d in list(files.items()):
        filename = d['filename']
        content = d['content']
        if 'mimetype' in d:
            mimetype = d['mimetype']
        else:
            mimetype = get_content_type(filename)
        if isinstance(name, str):
            name = name.encode('utf-8')
        if isinstance(filename, str):
            filename = filename.encode('utf-8')
        if isinstance(mimetype, str):
            mimetype = mimetype.encode('utf-8')
        if isinstance(content, str):
            content = content.encode('utf-8')
        output.append(b'--' + boundary)
        output.append(b'Content-Disposition: form-data; '
                      b'name="%b"; filename="%b"' % (name, filename))
        output.append(b'Content-Type: %b' % mimetype)
        output.append(b'')
        output.append(content)

    output.append(b'--' + boundary + b'--')
    output.append(b'')
    body = CRLF.join(output)
    headers = {
        'Content-Type': 'multipart/form-data; boundary=%s' % boundary.decode('ascii'),
    }
    return (headers, body)
