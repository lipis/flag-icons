# -*- coding: utf-8 -*-
"""
    werkzeug._internal
    ~~~~~~~~~~~~~~~~~~

    This module provides internally used helpers and constants.

    :copyright: (c) 2011 by the Werkzeug Team, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""
import inspect
from weakref import WeakKeyDictionary
from cStringIO import StringIO
from Cookie import SimpleCookie, Morsel, CookieError
from time import gmtime
from datetime import datetime, date


_logger = None
_empty_stream = StringIO('')
_signature_cache = WeakKeyDictionary()
_epoch_ord = date(1970, 1, 1).toordinal()


HTTP_STATUS_CODES = {
    100:    'Continue',
    101:    'Switching Protocols',
    102:    'Processing',
    200:    'OK',
    201:    'Created',
    202:    'Accepted',
    203:    'Non Authoritative Information',
    204:    'No Content',
    205:    'Reset Content',
    206:    'Partial Content',
    207:    'Multi Status',
    226:    'IM Used',              # see RFC 3229
    300:    'Multiple Choices',
    301:    'Moved Permanently',
    302:    'Found',
    303:    'See Other',
    304:    'Not Modified',
    305:    'Use Proxy',
    307:    'Temporary Redirect',
    400:    'Bad Request',
    401:    'Unauthorized',
    402:    'Payment Required',     # unused
    403:    'Forbidden',
    404:    'Not Found',
    405:    'Method Not Allowed',
    406:    'Not Acceptable',
    407:    'Proxy Authentication Required',
    408:    'Request Timeout',
    409:    'Conflict',
    410:    'Gone',
    411:    'Length Required',
    412:    'Precondition Failed',
    413:    'Request Entity Too Large',
    414:    'Request URI Too Long',
    415:    'Unsupported Media Type',
    416:    'Requested Range Not Satisfiable',
    417:    'Expectation Failed',
    418:    'I\'m a teapot',        # see RFC 2324
    422:    'Unprocessable Entity',
    423:    'Locked',
    424:    'Failed Dependency',
    426:    'Upgrade Required',
    449:    'Retry With',           # proprietary MS extension
    500:    'Internal Server Error',
    501:    'Not Implemented',
    502:    'Bad Gateway',
    503:    'Service Unavailable',
    504:    'Gateway Timeout',
    505:    'HTTP Version Not Supported',
    507:    'Insufficient Storage',
    510:    'Not Extended'
}


class _Missing(object):

    def __repr__(self):
        return 'no value'

    def __reduce__(self):
        return '_missing'

_missing = _Missing()


def _proxy_repr(cls):
    def proxy_repr(self):
        return '%s(%s)' % (self.__class__.__name__, cls.__repr__(self))
    return proxy_repr


def _get_environ(obj):
    env = getattr(obj, 'environ', obj)
    assert isinstance(env, dict), \
        '%r is not a WSGI environment (has to be a dict)' % type(obj).__name__
    return env


def _log(type, message, *args, **kwargs):
    """Log into the internal werkzeug logger."""
    global _logger
    if _logger is None:
        import logging
        _logger = logging.getLogger('werkzeug')
        # Only set up a default log handler if the
        # end-user application didn't set anything up.
        if not logging.root.handlers and _logger.level == logging.NOTSET:
            _logger.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            _logger.addHandler(handler)
    getattr(_logger, type)(message.rstrip(), *args, **kwargs)


def _parse_signature(func):
    """Return a signature object for the function."""
    if hasattr(func, 'im_func'):
        func = func.im_func

    # if we have a cached validator for this function, return it
    parse = _signature_cache.get(func)
    if parse is not None:
        return parse

    # inspect the function signature and collect all the information
    positional, vararg_var, kwarg_var, defaults = inspect.getargspec(func)
    defaults = defaults or ()
    arg_count = len(positional)
    arguments = []
    for idx, name in enumerate(positional):
        if isinstance(name, list):
            raise TypeError('cannot parse functions that unpack tuples '
                            'in the function signature')
        try:
            default = defaults[idx - arg_count]
        except IndexError:
            param = (name, False, None)
        else:
            param = (name, True, default)
        arguments.append(param)
    arguments = tuple(arguments)

    def parse(args, kwargs):
        new_args = []
        missing = []
        extra = {}

        # consume as many arguments as positional as possible
        for idx, (name, has_default, default) in enumerate(arguments):
            try:
                new_args.append(args[idx])
            except IndexError:
                try:
                    new_args.append(kwargs.pop(name))
                except KeyError:
                    if has_default:
                        new_args.append(default)
                    else:
                        missing.append(name)
            else:
                if name in kwargs:
                    extra[name] = kwargs.pop(name)

        # handle extra arguments
        extra_positional = args[arg_count:]
        if vararg_var is not None:
            new_args.extend(extra_positional)
            extra_positional = ()
        if kwargs and not kwarg_var is not None:
            extra.update(kwargs)
            kwargs = {}

        return new_args, kwargs, missing, extra, extra_positional, \
               arguments, vararg_var, kwarg_var
    _signature_cache[func] = parse
    return parse


def _patch_wrapper(old, new):
    """Helper function that forwards all the function details to the
    decorated function."""
    try:
        new.__name__ = old.__name__
        new.__module__ = old.__module__
        new.__doc__ = old.__doc__
        new.__dict__ = old.__dict__
    except Exception:
        pass
    return new


def _decode_unicode(value, charset, errors):
    """Like the regular decode function but this one raises an
    `HTTPUnicodeError` if errors is `strict`."""
    fallback = None
    if errors.startswith('fallback:'):
        fallback = errors[9:]
        errors = 'strict'
    try:
        return value.decode(charset, errors)
    except UnicodeError, e:
        if fallback is not None:
            return value.decode(fallback, 'replace')
        from werkzeug.exceptions import HTTPUnicodeError
        raise HTTPUnicodeError(str(e))


def _iter_modules(path):
    """Iterate over all modules in a package."""
    import os
    import pkgutil
    if hasattr(pkgutil, 'iter_modules'):
        for importer, modname, ispkg in pkgutil.iter_modules(path):
            yield modname, ispkg
        return
    from inspect import getmodulename
    from pydoc import ispackage
    found = set()
    for path in path:
        for filename in os.listdir(path):
            p = os.path.join(path, filename)
            modname = getmodulename(filename)
            if modname and modname != '__init__':
                if modname not in found:
                    found.add(modname)
                    yield modname, ispackage(modname)


def _dump_date(d, delim):
    """Used for `http_date` and `cookie_date`."""
    if d is None:
        d = gmtime()
    elif isinstance(d, datetime):
        d = d.utctimetuple()
    elif isinstance(d, (int, long, float)):
        d = gmtime(d)
    return '%s, %02d%s%s%s%s %02d:%02d:%02d GMT' % (
        ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')[d.tm_wday],
        d.tm_mday, delim,
        ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep',
         'Oct', 'Nov', 'Dec')[d.tm_mon - 1],
        delim, str(d.tm_year), d.tm_hour, d.tm_min, d.tm_sec
    )


def _date_to_unix(arg):
    """Converts a timetuple, integer or datetime object into the seconds from
    epoch in utc.
    """
    if isinstance(arg, datetime):
        arg = arg.utctimetuple()
    elif isinstance(arg, (int, long, float)):
        return int(arg)
    year, month, day, hour, minute, second = arg[:6]
    days = date(year, month, 1).toordinal() - _epoch_ord + day - 1
    hours = days * 24 + hour
    minutes = hours * 60 + minute
    seconds = minutes * 60 + second
    return seconds


class _ExtendedMorsel(Morsel):
    _reserved = {'httponly': 'HttpOnly'}
    _reserved.update(Morsel._reserved)

    def __init__(self, name=None, value=None):
        Morsel.__init__(self)
        if name is not None:
            self.set(name, value, value)

    def OutputString(self, attrs=None):
        httponly = self.pop('httponly', False)
        result = Morsel.OutputString(self, attrs).rstrip('\t ;')
        if httponly:
            result += '; HttpOnly'
        return result


class _ExtendedCookie(SimpleCookie):
    """Form of the base cookie that doesn't raise a `CookieError` for
    malformed keys.  This has the advantage that broken cookies submitted
    by nonstandard browsers don't cause the cookie to be empty.
    """

    def _BaseCookie__set(self, key, real_value, coded_value):
        morsel = self.get(key, _ExtendedMorsel())
        try:
            morsel.set(key, real_value, coded_value)
        except CookieError:
            pass
        dict.__setitem__(self, key, morsel)


class _DictAccessorProperty(object):
    """Baseclass for `environ_property` and `header_property`."""
    read_only = False

    def __init__(self, name, default=None, load_func=None, dump_func=None,
                 read_only=None, doc=None):
        self.name = name
        self.default = default
        self.load_func = load_func
        self.dump_func = dump_func
        if read_only is not None:
            self.read_only = read_only
        self.__doc__ = doc

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        storage = self.lookup(obj)
        if self.name not in storage:
            return self.default
        rv = storage[self.name]
        if self.load_func is not None:
            try:
                rv = self.load_func(rv)
            except (ValueError, TypeError):
                rv = self.default
        return rv

    def __set__(self, obj, value):
        if self.read_only:
            raise AttributeError('read only property')
        if self.dump_func is not None:
            value = self.dump_func(value)
        self.lookup(obj)[self.name] = value

    def __delete__(self, obj):
        if self.read_only:
            raise AttributeError('read only property')
        self.lookup(obj).pop(self.name, None)

    def __repr__(self):
        return '<%s %s>' % (
            self.__class__.__name__,
            self.name
        )


def _easteregg(app):
    """Like the name says.  But who knows how it works?"""
    gyver = '\n'.join([x + (77 - len(x)) * ' ' for x in '''
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
7f2zLkGNv8b191cD/3vs9Q833z8t'''.decode('base64').decode('zlib').splitlines()])
    def easteregged(environ, start_response):
        def injecting_start_response(status, headers, exc_info=None):
            headers.append(('X-Powered-By', 'Werkzeug'))
            return start_response(status, headers, exc_info)
        if environ.get('QUERY_STRING') != 'macgybarchakku':
            return app(environ, injecting_start_response)
        injecting_start_response('200 OK', [('Content-Type', 'text/html')])
        return ['''
<!DOCTYPE html>
<html>
<head>
<title>About Werkzeug</title>
<style type="text/css">
  body { font: 15px Georgia, serif; text-align: center; }
  a { color: #333; text-decoration: none; }
  h1 { font-size: 30px; margin: 20px 0 10px 0; }
  p { margin: 0 0 30px 0; }
  pre { font: 11px 'Consolas', 'Monaco', monospace; line-height: 0.95; }
</style>
</head>
<body>
<h1><a href="http://werkzeug.pocoo.org/">Werkzeug</a></h1>
<p>the Swiss Army knife of Python web development.</p>
<pre>%s\n\n\n</pre>
</body>
</html>''' % gyver]
    return easteregged
