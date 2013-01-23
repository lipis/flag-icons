import sys

if sys.version_info[0] >= 3:
    text_type = str
    string_types = str,
    iteritems = lambda o: o.items()
    itervalues = lambda o: o.values()
    izip = zip

else:
    text_type = unicode
    string_types = basestring,
    iteritems = lambda o: o.iteritems()
    itervalues = lambda o: o.itervalues()
    from itertools import izip

def with_metaclass(meta, base=object):
    return meta("NewBase", (base,), {})

