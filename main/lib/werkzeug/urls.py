# -*- coding: utf-8 -*-
"""
    werkzeug.urls
    ~~~~~~~~~~~~~

    This module implements various URL related functions.

    :copyright: (c) 2011 by the Werkzeug Team, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""
import urlparse

from werkzeug._internal import _decode_unicode
from werkzeug.datastructures import MultiDict, iter_multi_items
from werkzeug.wsgi import make_chunk_iter


#: list of characters that are always safe in URLs.
_always_safe = ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                'abcdefghijklmnopqrstuvwxyz'
                '0123456789_.-')
_safe_map = dict((c, c) for c in _always_safe)
for i in xrange(0x80):
    c = chr(i)
    if c not in _safe_map:
        _safe_map[c] = '%%%02X' % i
_safe_map.update((chr(i), '%%%02X' % i) for i in xrange(0x80, 0x100))
_safemaps = {}

#: lookup table for encoded characters.
_hexdig = '0123456789ABCDEFabcdef'
_hextochr = dict((a + b, chr(int(a + b, 16)))
                 for a in _hexdig for b in _hexdig)


def _quote(s, safe='/', _join=''.join):
    assert isinstance(s, str), 'quote only works on bytes'
    if not s or not s.rstrip(_always_safe + safe):
        return s
    try:
        quoter = _safemaps[safe]
    except KeyError:
        safe_map = _safe_map.copy()
        safe_map.update([(c, c) for c in safe])
        _safemaps[safe] = quoter = safe_map.__getitem__
    return _join(map(quoter, s))


def _quote_plus(s, safe=''):
    if ' ' in s:
        return _quote(s, safe + ' ').replace(' ', '+')
    return _quote(s, safe)


def _safe_urlsplit(s):
    """the urlparse.urlsplit cache breaks if it contains unicode and
    we cannot control that.  So we force type cast that thing back
    to what we think it is.
    """
    rv = urlparse.urlsplit(s)
    # we have to check rv[2] here and not rv[1] as rv[1] will be
    # an empty bytestring in case no domain was given.
    if type(rv[2]) is not type(s):
        assert hasattr(urlparse, 'clear_cache')
        urlparse.clear_cache()
        rv = urlparse.urlsplit(s)
        assert type(rv[2]) is type(s)
    return rv


def _unquote(s, unsafe=''):
    assert isinstance(s, str), 'unquote only works on bytes'
    rv = s.split('%')
    if len(rv) == 1:
        return s
    s = rv[0]
    for item in rv[1:]:
        try:
            char = _hextochr[item[:2]]
            if char in unsafe:
                raise KeyError()
            s += char + item[2:]
        except KeyError:
            s += '%' + item
    return s


def _unquote_plus(s):
    return _unquote(s.replace('+', ' '))


def _uri_split(uri):
    """Splits up an URI or IRI."""
    scheme, netloc, path, query, fragment = _safe_urlsplit(uri)

    port = None

    if '@' in netloc:
        auth, hostname = netloc.split('@', 1)
    else:
        auth = None
        hostname = netloc
    if hostname:
        if ':' in hostname:
            hostname, port = hostname.split(':', 1)
    return scheme, auth, hostname, port, path, query, fragment


def iri_to_uri(iri, charset='utf-8'):
    r"""Converts any unicode based IRI to an acceptable ASCII URI.  Werkzeug
    always uses utf-8 URLs internally because this is what browsers and HTTP
    do as well.  In some places where it accepts an URL it also accepts a
    unicode IRI and converts it into a URI.

    Examples for IRI versus URI:

    >>> iri_to_uri(u'http://☃.net/')
    'http://xn--n3h.net/'
    >>> iri_to_uri(u'http://üser:pässword@☃.net/påth')
    'http://%C3%BCser:p%C3%A4ssword@xn--n3h.net/p%C3%A5th'

    .. versionadded:: 0.6

    :param iri: the iri to convert
    :param charset: the charset for the URI
    """
    iri = unicode(iri)
    scheme, auth, hostname, port, path, query, fragment = _uri_split(iri)

    scheme = scheme.encode('ascii')
    hostname = hostname.encode('idna')
    if auth:
        if ':' in auth:
            auth, password = auth.split(':', 1)
        else:
            password = None
        auth = _quote(auth.encode(charset))
        if password:
            auth += ':' + _quote(password.encode(charset))
        hostname = auth + '@' + hostname
    if port:
        hostname += ':' + port

    path = _quote(path.encode(charset), safe="/:~+")
    query = _quote(query.encode(charset), safe="=%&[]:;$()+,!?*/")

    # this absolutely always must return a string.  Otherwise some parts of
    # the system might perform double quoting (#61)
    return str(urlparse.urlunsplit([scheme, hostname, path, query, fragment]))


def uri_to_iri(uri, charset='utf-8', errors='replace'):
    r"""Converts a URI in a given charset to a IRI.

    Examples for URI versus IRI

    >>> uri_to_iri('http://xn--n3h.net/')
    u'http://\u2603.net/'
    >>> uri_to_iri('http://%C3%BCser:p%C3%A4ssword@xn--n3h.net/p%C3%A5th')
    u'http://\xfcser:p\xe4ssword@\u2603.net/p\xe5th'

    Query strings are left unchanged:

    >>> uri_to_iri('/?foo=24&x=%26%2f')
    u'/?foo=24&x=%26%2f'

    .. versionadded:: 0.6

    :param uri: the URI to convert
    :param charset: the charset of the URI
    :param errors: the error handling on decode
    """
    uri = url_fix(str(uri), charset)
    scheme, auth, hostname, port, path, query, fragment = _uri_split(uri)

    scheme = _decode_unicode(scheme, 'ascii', errors)

    try:
        hostname = hostname.decode('idna')
    except UnicodeError:
        # dammit, that codec raised an error.  Because it does not support
        # any error handling we have to fake it.... badly
        if errors not in ('ignore', 'replace'):
            raise
        hostname = hostname.decode('ascii', errors)

    if auth:
        if ':' in auth:
            auth, password = auth.split(':', 1)
        else:
            password = None
        auth = _decode_unicode(_unquote(auth), charset, errors)
        if password:
            auth += u':' + _decode_unicode(_unquote(password),
                                           charset, errors)
        hostname = auth + u'@' + hostname
    if port:
        # port should be numeric, but you never know...
        hostname += u':' + port.decode(charset, errors)

    path = _decode_unicode(_unquote(path, '/;?'), charset, errors)
    query = _decode_unicode(_unquote(query, ';/?:@&=+,$'),
                            charset, errors)

    return urlparse.urlunsplit([scheme, hostname, path, query, fragment])


def url_decode(s, charset='utf-8', decode_keys=False, include_empty=True,
               errors='replace', separator='&', cls=None):
    """Parse a querystring and return it as :class:`MultiDict`.  Per default
    only values are decoded into unicode strings.  If `decode_keys` is set to
    `True` the same will happen for keys.

    Per default a missing value for a key will default to an empty key.  If
    you don't want that behavior you can set `include_empty` to `False`.

    Per default encoding errors are ignored.  If you want a different behavior
    you can set `errors` to ``'replace'`` or ``'strict'``.  In strict mode a
    `HTTPUnicodeError` is raised.

    .. versionchanged:: 0.5
       In previous versions ";" and "&" could be used for url decoding.
       This changed in 0.5 where only "&" is supported.  If you want to
       use ";" instead a different `separator` can be provided.

       The `cls` parameter was added.

    :param s: a string with the query string to decode.
    :param charset: the charset of the query string.
    :param decode_keys: set to `True` if you want the keys to be decoded
                        as well.
    :param include_empty: Set to `False` if you don't want empty values to
                          appear in the dict.
    :param errors: the decoding error behavior.
    :param separator: the pair separator to be used, defaults to ``&``
    :param cls: an optional dict class to use.  If this is not specified
                       or `None` the default :class:`MultiDict` is used.
    """
    if cls is None:
        cls = MultiDict
    return cls(_url_decode_impl(str(s).split(separator), charset, decode_keys,
                                include_empty, errors))


def url_decode_stream(stream, charset='utf-8', decode_keys=False,
                      include_empty=True, errors='replace', separator='&',
                      cls=None, limit=None, return_iterator=False):
    """Works like :func:`url_decode` but decodes a stream.  The behavior
    of stream and limit follows functions like
    :func:`~werkzeug.wsgi.make_line_iter`.  The generator of pairs is
    directly fed to the `cls` so you can consume the data while it's
    parsed.

    .. versionadded:: 0.8

    :param stream: a stream with the encoded querystring
    :param charset: the charset of the query string.
    :param decode_keys: set to `True` if you want the keys to be decoded
                        as well.
    :param include_empty: Set to `False` if you don't want empty values to
                          appear in the dict.
    :param errors: the decoding error behavior.
    :param separator: the pair separator to be used, defaults to ``&``
    :param cls: an optional dict class to use.  If this is not specified
                       or `None` the default :class:`MultiDict` is used.
    :param limit: the content length of the URL data.  Not necessary if
                  a limited stream is provided.
    :param return_iterator: if set to `True` the `cls` argument is ignored
                            and an iterator over all decoded pairs is
                            returned
    """
    if return_iterator:
        cls = lambda x: x
    elif cls is None:
        cls = MultiDict
    pair_iter = make_chunk_iter(stream, separator, limit)
    return cls(_url_decode_impl(pair_iter, charset, decode_keys,
                                include_empty, errors))


def _url_decode_impl(pair_iter, charset, decode_keys, include_empty,
                     errors):
    for pair in pair_iter:
        if not pair:
            continue
        if '=' in pair:
            key, value = pair.split('=', 1)
        else:
            if not include_empty:
                continue
            key = pair
            value = ''
        key = _unquote_plus(key)
        if decode_keys:
            key = _decode_unicode(key, charset, errors)
        yield key, url_unquote_plus(value, charset, errors)


def url_encode(obj, charset='utf-8', encode_keys=False, sort=False, key=None,
               separator='&'):
    """URL encode a dict/`MultiDict`.  If a value is `None` it will not appear
    in the result string.  Per default only values are encoded into the target
    charset strings.  If `encode_keys` is set to ``True`` unicode keys are
    supported too.

    If `sort` is set to `True` the items are sorted by `key` or the default
    sorting algorithm.

    .. versionadded:: 0.5
        `sort`, `key`, and `separator` were added.

    :param obj: the object to encode into a query string.
    :param charset: the charset of the query string.
    :param encode_keys: set to `True` if you have unicode keys.
    :param sort: set to `True` if you want parameters to be sorted by `key`.
    :param separator: the separator to be used for the pairs.
    :param key: an optional function to be used for sorting.  For more details
                check out the :func:`sorted` documentation.
    """
    return separator.join(_url_encode_impl(obj, charset, encode_keys, sort, key))


def url_encode_stream(obj, stream=None, charset='utf-8', encode_keys=False,
                      sort=False, key=None, separator='&'):
    """Like :meth:`url_encode` but writes the results to a stream
    object.  If the stream is `None` a generator over all encoded
    pairs is returned.

    .. versionadded:: 0.8

    :param obj: the object to encode into a query string.
    :param stream: a stream to write the encoded object into or `None` if
                   an iterator over the encoded pairs should be returned.  In
                   that case the separator argument is ignored.
    :param charset: the charset of the query string.
    :param encode_keys: set to `True` if you have unicode keys.
    :param sort: set to `True` if you want parameters to be sorted by `key`.
    :param separator: the separator to be used for the pairs.
    :param key: an optional function to be used for sorting.  For more details
                check out the :func:`sorted` documentation.
    """
    gen = _url_encode_impl(obj, charset, encode_keys, sort, key)
    if stream is None:
        return gen
    for idx, chunk in enumerate(gen):
        if idx:
            stream.write(separator)
        stream.write(chunk)


def _url_encode_impl(obj, charset, encode_keys, sort, key):
    iterable = iter_multi_items(obj)
    if sort:
        iterable = sorted(iterable, key=key)
    for key, value in iterable:
        if value is None:
            continue
        if encode_keys and isinstance(key, unicode):
            key = key.encode(charset)
        else:
            key = str(key)
        if isinstance(value, unicode):
            value = value.encode(charset)
        else:
            value = str(value)
        yield '%s=%s' % (_quote(key), _quote_plus(value))


def url_quote(s, charset='utf-8', safe='/:'):
    """URL encode a single string with a given encoding.

    :param s: the string to quote.
    :param charset: the charset to be used.
    :param safe: an optional sequence of safe characters.
    """
    if isinstance(s, unicode):
        s = s.encode(charset)
    elif not isinstance(s, str):
        s = str(s)
    return _quote(s, safe=safe)


def url_quote_plus(s, charset='utf-8', safe=''):
    """URL encode a single string with the given encoding and convert
    whitespace to "+".

    :param s: the string to quote.
    :param charset: the charset to be used.
    :param safe: an optional sequence of safe characters.
    """
    if isinstance(s, unicode):
        s = s.encode(charset)
    elif not isinstance(s, str):
        s = str(s)
    return _quote_plus(s, safe=safe)


def url_unquote(s, charset='utf-8', errors='replace'):
    """URL decode a single string with a given decoding.

    Per default encoding errors are ignored.  If you want a different behavior
    you can set `errors` to ``'replace'`` or ``'strict'``.  In strict mode a
    `HTTPUnicodeError` is raised.

    :param s: the string to unquote.
    :param charset: the charset to be used.
    :param errors: the error handling for the charset decoding.
    """
    if isinstance(s, unicode):
        s = s.encode(charset)
    return _decode_unicode(_unquote(s), charset, errors)


def url_unquote_plus(s, charset='utf-8', errors='replace'):
    """URL decode a single string with the given decoding and decode
    a "+" to whitespace.

    Per default encoding errors are ignored.  If you want a different behavior
    you can set `errors` to ``'replace'`` or ``'strict'``.  In strict mode a
    `HTTPUnicodeError` is raised.

    :param s: the string to unquote.
    :param charset: the charset to be used.
    :param errors: the error handling for the charset decoding.
    """
    if isinstance(s, unicode):
        s = s.encode(charset)
    return _decode_unicode(_unquote_plus(s), charset, errors)


def url_fix(s, charset='utf-8'):
    r"""Sometimes you get an URL by a user that just isn't a real URL because
    it contains unsafe characters like ' ' and so on.  This function can fix
    some of the problems in a similar way browsers handle data entered by the
    user:

    >>> url_fix(u'http://de.wikipedia.org/wiki/Elf (Begriffskl\xe4rung)')
    'http://de.wikipedia.org/wiki/Elf%20%28Begriffskl%C3%A4rung%29'

    :param s: the string with the URL to fix.
    :param charset: The target charset for the URL if the url was given as
                    unicode string.
    """
    if isinstance(s, unicode):
        s = s.encode(charset, 'replace')
    scheme, netloc, path, qs, anchor = _safe_urlsplit(s)
    path = _quote(path, '/%')
    qs = _quote_plus(qs, ':&%=')
    return urlparse.urlunsplit((scheme, netloc, path, qs, anchor))


class Href(object):
    """Implements a callable that constructs URLs with the given base. The
    function can be called with any number of positional and keyword
    arguments which than are used to assemble the URL.  Works with URLs
    and posix paths.

    Positional arguments are appended as individual segments to
    the path of the URL:

    >>> href = Href('/foo')
    >>> href('bar', 23)
    '/foo/bar/23'
    >>> href('foo', bar=23)
    '/foo/foo?bar=23'

    If any of the arguments (positional or keyword) evaluates to `None` it
    will be skipped.  If no keyword arguments are given the last argument
    can be a :class:`dict` or :class:`MultiDict` (or any other dict subclass),
    otherwise the keyword arguments are used for the query parameters, cutting
    off the first trailing underscore of the parameter name:

    >>> href(is_=42)
    '/foo?is=42'
    >>> href({'foo': 'bar'})
    '/foo?foo=bar'

    Combining of both methods is not allowed:

    >>> href({'foo': 'bar'}, bar=42)
    Traceback (most recent call last):
      ...
    TypeError: keyword arguments and query-dicts can't be combined

    Accessing attributes on the href object creates a new href object with
    the attribute name as prefix:

    >>> bar_href = href.bar
    >>> bar_href("blub")
    '/foo/bar/blub'

    If `sort` is set to `True` the items are sorted by `key` or the default
    sorting algorithm:

    >>> href = Href("/", sort=True)
    >>> href(a=1, b=2, c=3)
    '/?a=1&b=2&c=3'

    .. versionadded:: 0.5
        `sort` and `key` were added.
    """

    def __init__(self, base='./', charset='utf-8', sort=False, key=None):
        if not base:
            base = './'
        self.base = base
        self.charset = charset
        self.sort = sort
        self.key = key

    def __getattr__(self, name):
        if name[:2] == '__':
            raise AttributeError(name)
        base = self.base
        if base[-1:] != '/':
            base += '/'
        return Href(urlparse.urljoin(base, name), self.charset, self.sort,
                    self.key)

    def __call__(self, *path, **query):
        if path and isinstance(path[-1], dict):
            if query:
                raise TypeError('keyword arguments and query-dicts '
                                'can\'t be combined')
            query, path = path[-1], path[:-1]
        elif query:
            query = dict([(k.endswith('_') and k[:-1] or k, v)
                          for k, v in query.items()])
        path = '/'.join([url_quote(x, self.charset) for x in path
                         if x is not None]).lstrip('/')
        rv = self.base
        if path:
            if not rv.endswith('/'):
                rv += '/'
            rv = urlparse.urljoin(rv, './' + path)
        if query:
            rv += '?' + url_encode(query, self.charset, sort=self.sort,
                                   key=self.key)
        return str(rv)
