# -*- coding: utf-8 -*-
#
# Copyright (C) 2007 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://babel.edgewall.org/wiki/License.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://babel.edgewall.org/log/.

"""Low-level locale data access.

:note: The `Locale` class, which uses this module under the hood, provides a
       more convenient interface for accessing the locale data.
"""

import os
import pickle
try:
    import threading
except ImportError:
    import dummy_threading as threading
from UserDict import DictMixin

__all__ = ['exists', 'list', 'load']
__docformat__ = 'restructuredtext en'

_cache = {}
_cache_lock = threading.RLock()
_dirname = os.path.join(os.path.dirname(__file__), 'localedata')


def exists(name):
    """Check whether locale data is available for the given locale.
    
    :param name: the locale identifier string
    :return: `True` if the locale data exists, `False` otherwise
    :rtype: `bool`
    """
    if name in _cache:
        return True
    return os.path.exists(os.path.join(_dirname, '%s.dat' % name))


def list():
    """Return a list of all locale identifiers for which locale data is
    available.
    
    :return: a list of locale identifiers (strings)
    :rtype: `list`
    :since: version 0.8.1
    """
    return [stem for stem, extension in [
        os.path.splitext(filename) for filename in os.listdir(_dirname)
    ] if extension == '.dat' and stem != 'root']


def load(name, merge_inherited=True):
    """Load the locale data for the given locale.
    
    The locale data is a dictionary that contains much of the data defined by
    the Common Locale Data Repository (CLDR). This data is stored as a
    collection of pickle files inside the ``babel`` package.
    
    >>> d = load('en_US')
    >>> d['languages']['sv']
    u'Swedish'
    
    Note that the results are cached, and subsequent requests for the same
    locale return the same dictionary:
    
    >>> d1 = load('en_US')
    >>> d2 = load('en_US')
    >>> d1 is d2
    True
    
    :param name: the locale identifier string (or "root")
    :param merge_inherited: whether the inherited data should be merged into
                            the data of the requested locale
    :return: the locale data
    :rtype: `dict`
    :raise `IOError`: if no locale data file is found for the given locale
                      identifer, or one of the locales it inherits from
    """
    _cache_lock.acquire()
    try:
        data = _cache.get(name)
        if not data:
            # Load inherited data
            if name == 'root' or not merge_inherited:
                data = {}
            else:
                parts = name.split('_')
                if len(parts) == 1:
                    parent = 'root'
                else:
                    parent = '_'.join(parts[:-1])
                data = load(parent).copy()
            filename = os.path.join(_dirname, '%s.dat' % name)
            fileobj = open(filename, 'rb')
            try:
                if name != 'root' and merge_inherited:
                    merge(data, pickle.load(fileobj))
                else:
                    data = pickle.load(fileobj)
                _cache[name] = data
            finally:
                fileobj.close()
        return data
    finally:
        _cache_lock.release()


def merge(dict1, dict2):
    """Merge the data from `dict2` into the `dict1` dictionary, making copies
    of nested dictionaries.
    
    >>> d = {1: 'foo', 3: 'baz'}
    >>> merge(d, {1: 'Foo', 2: 'Bar'})
    >>> items = d.items(); items.sort(); items
    [(1, 'Foo'), (2, 'Bar'), (3, 'baz')]
    
    :param dict1: the dictionary to merge into
    :param dict2: the dictionary containing the data that should be merged
    """
    for key, val2 in dict2.items():
        if val2 is not None:
            val1 = dict1.get(key)
            if isinstance(val2, dict):
                if val1 is None:
                    val1 = {}
                if isinstance(val1, Alias):
                    val1 = (val1, val2)
                elif isinstance(val1, tuple):
                    alias, others = val1
                    others = others.copy()
                    merge(others, val2)
                    val1 = (alias, others)
                else:
                    val1 = val1.copy()
                    merge(val1, val2)
            else:
                val1 = val2
            dict1[key] = val1


class Alias(object):
    """Representation of an alias in the locale data.
    
    An alias is a value that refers to some other part of the locale data,
    as specified by the `keys`.
    """

    def __init__(self, keys):
        self.keys = tuple(keys)

    def __repr__(self):
        return '<%s %r>' % (type(self).__name__, self.keys)

    def resolve(self, data):
        """Resolve the alias based on the given data.
        
        This is done recursively, so if one alias resolves to a second alias,
        that second alias will also be resolved.
        
        :param data: the locale data
        :type data: `dict`
        """
        base = data
        for key in self.keys:
            data = data[key]
        if isinstance(data, Alias):
            data = data.resolve(base)
        elif isinstance(data, tuple):
            alias, others = data
            data = alias.resolve(base)
        return data


class LocaleDataDict(DictMixin, dict):
    """Dictionary wrapper that automatically resolves aliases to the actual
    values.
    """

    def __init__(self, data, base=None):
        dict.__init__(self, data)
        if base is None:
            base = data
        self.base = base

    def __getitem__(self, key):
        orig = val = dict.__getitem__(self, key)
        if isinstance(val, Alias): # resolve an alias
            val = val.resolve(self.base)
        if isinstance(val, tuple): # Merge a partial dict with an alias
            alias, others = val
            val = alias.resolve(self.base).copy()
            merge(val, others)
        if type(val) is dict: # Return a nested alias-resolving dict
            val = LocaleDataDict(val, base=self.base)
        if val is not orig:
            self[key] = val
        return val

    def copy(self):
        return LocaleDataDict(dict.copy(self), base=self.base)
