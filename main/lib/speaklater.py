# -*- coding: utf-8 -*-
r"""
    speaklater
    ~~~~~~~~~~

    A module that provides lazy strings for translations.  Basically you
    get an object that appears to be a string but changes the value every
    time the value is evaluated based on a callable you provide.

    For example you can have a global `lazy_gettext` function that returns
    a lazy string with the value of the current set language.

    Example:

    >>> from speaklater import make_lazy_string
    >>> sval = u'Hello World'
    >>> string = make_lazy_string(lambda: sval)

    This lazy string will evaluate to the value of the `sval` variable.

    >>> string
    lu'Hello World'
    >>> unicode(string)
    u'Hello World'
    >>> string.upper()
    u'HELLO WORLD'

    If you change the value, the lazy string will change as well:

    >>> sval = u'Hallo Welt'
    >>> string.upper()
    u'HALLO WELT'

    This is especially handy when combined with a thread local and gettext
    translations or dicts of translatable strings:

    >>> from speaklater import make_lazy_gettext
    >>> from threading import local
    >>> l = local()
    >>> l.translations = {u'Yes': 'Ja'}
    >>> lazy_gettext = make_lazy_gettext(lambda: l.translations.get)
    >>> yes = lazy_gettext(u'Yes')
    >>> print yes
    Ja
    >>> l.translations[u'Yes'] = u'Si'
    >>> print yes
    Si

    Lazy strings are no real strings so if you pass this sort of string to
    a function that performs an instance check, it will fail.  In that case
    you have to explicitly convert it with `unicode` and/or `string` depending
    on what string type the lazy string encapsulates.

    To check if a string is lazy, you can use the `is_lazy_string` function:

    >>> from speaklater import is_lazy_string
    >>> is_lazy_string(u'yes')
    False
    >>> is_lazy_string(yes)
    True

    New in version 1.2: It's now also possible to pass keyword arguments to
    the callback used with `make_lazy_string`.

    :copyright: (c) 2010 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""


def is_lazy_string(obj):
    """Checks if the given object is a lazy string."""
    return isinstance(obj, _LazyString)


def make_lazy_string(__func, *args, **kwargs):
    """Creates a lazy string by invoking func with args."""
    return _LazyString(__func, args, kwargs)


def make_lazy_gettext(lookup_func):
    """Creates a lazy gettext function dispatches to a gettext
    function as returned by `lookup_func`.

    Example:

    >>> translations = {u'Yes': u'Ja'}
    >>> lazy_gettext = make_lazy_gettext(lambda: translations.get)
    >>> x = lazy_gettext(u'Yes')
    >>> x
    lu'Ja'
    >>> translations[u'Yes'] = u'Si'
    >>> x
    lu'Si'
    """
    def lazy_gettext(string):
        if is_lazy_string(string):
            return string
        return make_lazy_string(lookup_func(), string)
    return lazy_gettext


class _LazyString(object):
    """Class for strings created by a function call.

    The proxy implementation attempts to be as complete as possible, so that
    the lazy objects should mostly work as expected, for example for sorting.
    """
    __slots__ = ('_func', '_args', '_kwargs')

    def __init__(self, func, args, kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs

    value = property(lambda x: x._func(*x._args, **x._kwargs))

    def __contains__(self, key):
        return key in self.value

    def __nonzero__(self):
        return bool(self.value)

    def __dir__(self):
        return dir(unicode)

    def __iter__(self):
        return iter(self.value)

    def __len__(self):
        return len(self.value)

    def __str__(self):
        return str(self.value)

    def __unicode__(self):
        return unicode(self.value)

    def __add__(self, other):
        return self.value + other

    def __radd__(self, other):
        return other + self.value

    def __mod__(self, other):
        return self.value % other

    def __rmod__(self, other):
        return other % self.value

    def __mul__(self, other):
        return self.value * other

    def __rmul__(self, other):
        return other * self.value

    def __lt__(self, other):
        return self.value < other

    def __le__(self, other):
        return self.value <= other

    def __eq__(self, other):
        return self.value == other

    def __ne__(self, other):
        return self.value != other

    def __gt__(self, other):
        return self.value > other

    def __ge__(self, other):
        return self.value >= other

    def __getattr__(self, name):
        if name == '__members__':
            return self.__dir__()
        return getattr(self.value, name)

    def __getstate__(self):
        return self._func, self._args, self._kwargs

    def __setstate__(self, tup):
        self._func, self._args, self._kwargs = tup

    def __getitem__(self, key):
        return self.value[key]

    def __copy__(self):
        return self

    def __repr__(self):
        try:
            return 'l' + repr(self.value)
        except Exception:
            return '<%s broken>' % self.__class__.__name__


if __name__ == '__main__':
    import doctest
    doctest.testmod()
