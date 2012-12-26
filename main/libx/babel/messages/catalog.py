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

"""Data structures for message catalogs."""

from cgi import parse_header
from datetime import datetime
from difflib import get_close_matches
from email import message_from_string
from copy import copy
import re
import time

from babel import __version__ as VERSION
from babel.core import Locale
from babel.dates import format_datetime
from babel.messages.plurals import get_plural
from babel.util import odict, distinct, set, LOCALTZ, UTC, FixedOffsetTimezone

__all__ = ['Message', 'Catalog', 'TranslationError']
__docformat__ = 'restructuredtext en'


PYTHON_FORMAT = re.compile(r'''(?x)
    \%
        (?:\(([\w]*)\))?
        (
            [-#0\ +]?(?:\*|[\d]+)?
            (?:\.(?:\*|[\d]+))?
            [hlL]?
        )
        ([diouxXeEfFgGcrs%])
''')


class Message(object):
    """Representation of a single message in a catalog."""

    def __init__(self, id, string=u'', locations=(), flags=(), auto_comments=(),
                 user_comments=(), previous_id=(), lineno=None):
        """Create the message object.

        :param id: the message ID, or a ``(singular, plural)`` tuple for
                   pluralizable messages
        :param string: the translated message string, or a
                       ``(singular, plural)`` tuple for pluralizable messages
        :param locations: a sequence of ``(filenname, lineno)`` tuples
        :param flags: a set or sequence of flags
        :param auto_comments: a sequence of automatic comments for the message
        :param user_comments: a sequence of user comments for the message
        :param previous_id: the previous message ID, or a ``(singular, plural)``
                            tuple for pluralizable messages
        :param lineno: the line number on which the msgid line was found in the
                       PO file, if any
        """
        self.id = id #: The message ID
        if not string and self.pluralizable:
            string = (u'', u'')
        self.string = string #: The message translation
        self.locations = list(distinct(locations))
        self.flags = set(flags)
        if id and self.python_format:
            self.flags.add('python-format')
        else:
            self.flags.discard('python-format')
        self.auto_comments = list(distinct(auto_comments))
        self.user_comments = list(distinct(user_comments))
        if isinstance(previous_id, basestring):
            self.previous_id = [previous_id]
        else:
            self.previous_id = list(previous_id)
        self.lineno = lineno

    def __repr__(self):
        return '<%s %r (flags: %r)>' % (type(self).__name__, self.id,
                                        list(self.flags))

    def __cmp__(self, obj):
        """Compare Messages, taking into account plural ids"""
        if isinstance(obj, Message):
            plural = self.pluralizable
            obj_plural = obj.pluralizable
            if plural and obj_plural:
                return cmp(self.id[0], obj.id[0])
            elif plural:
                return cmp(self.id[0], obj.id)
            elif obj_plural:
                return cmp(self.id, obj.id[0])
        return cmp(self.id, obj.id)

    def clone(self):
        return Message(*map(copy, (self.id, self.string, self.locations,
                                   self.flags, self.auto_comments,
                                   self.user_comments, self.previous_id,
                                   self.lineno)))

    def check(self, catalog=None):
        """Run various validation checks on the message.  Some validations
        are only performed if the catalog is provided.  This method returns
        a sequence of `TranslationError` objects.

        :rtype: ``iterator``
        :param catalog: A catalog instance that is passed to the checkers
        :see: `Catalog.check` for a way to perform checks for all messages
              in a catalog.
        """
        from babel.messages.checkers import checkers
        errors = []
        for checker in checkers:
            try:
                checker(catalog, self)
            except TranslationError, e:
                errors.append(e)
        return errors

    def fuzzy(self):
        return 'fuzzy' in self.flags
    fuzzy = property(fuzzy, doc="""\
        Whether the translation is fuzzy.

        >>> Message('foo').fuzzy
        False
        >>> msg = Message('foo', 'foo', flags=['fuzzy'])
        >>> msg.fuzzy
        True
        >>> msg
        <Message 'foo' (flags: ['fuzzy'])>

        :type:  `bool`
        """)

    def pluralizable(self):
        return isinstance(self.id, (list, tuple))
    pluralizable = property(pluralizable, doc="""\
        Whether the message is plurizable.

        >>> Message('foo').pluralizable
        False
        >>> Message(('foo', 'bar')).pluralizable
        True

        :type:  `bool`
        """)

    def python_format(self):
        ids = self.id
        if not isinstance(ids, (list, tuple)):
            ids = [ids]
        return bool(filter(None, [PYTHON_FORMAT.search(id) for id in ids]))
    python_format = property(python_format, doc="""\
        Whether the message contains Python-style parameters.

        >>> Message('foo %(name)s bar').python_format
        True
        >>> Message(('foo %(name)s', 'foo %(name)s')).python_format
        True

        :type:  `bool`
        """)


class TranslationError(Exception):
    """Exception thrown by translation checkers when invalid message
    translations are encountered."""


DEFAULT_HEADER = u"""\
# Translations template for PROJECT.
# Copyright (C) YEAR ORGANIZATION
# This file is distributed under the same license as the PROJECT project.
# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.
#"""


class Catalog(object):
    """Representation of a message catalog."""

    def __init__(self, locale=None, domain=None, header_comment=DEFAULT_HEADER,
                 project=None, version=None, copyright_holder=None,
                 msgid_bugs_address=None, creation_date=None,
                 revision_date=None, last_translator=None, language_team=None,
                 charset='utf-8', fuzzy=True):
        """Initialize the catalog object.

        :param locale: the locale identifier or `Locale` object, or `None`
                       if the catalog is not bound to a locale (which basically
                       means it's a template)
        :param domain: the message domain
        :param header_comment: the header comment as string, or `None` for the
                               default header
        :param project: the project's name
        :param version: the project's version
        :param copyright_holder: the copyright holder of the catalog
        :param msgid_bugs_address: the email address or URL to submit bug
                                   reports to
        :param creation_date: the date the catalog was created
        :param revision_date: the date the catalog was revised
        :param last_translator: the name and email of the last translator
        :param language_team: the name and email of the language team
        :param charset: the encoding to use in the output
        :param fuzzy: the fuzzy bit on the catalog header
        """
        self.domain = domain #: The message domain
        if locale:
            locale = Locale.parse(locale)
        self.locale = locale #: The locale or `None`
        self._header_comment = header_comment
        self._messages = odict()

        self.project = project or 'PROJECT' #: The project name
        self.version = version or 'VERSION' #: The project version
        self.copyright_holder = copyright_holder or 'ORGANIZATION'
        self.msgid_bugs_address = msgid_bugs_address or 'EMAIL@ADDRESS'

        self.last_translator = last_translator or 'FULL NAME <EMAIL@ADDRESS>'
        """Name and email address of the last translator."""
        self.language_team = language_team or 'LANGUAGE <LL@li.org>'
        """Name and email address of the language team."""

        self.charset = charset or 'utf-8'

        if creation_date is None:
            creation_date = datetime.now(LOCALTZ)
        elif isinstance(creation_date, datetime) and not creation_date.tzinfo:
            creation_date = creation_date.replace(tzinfo=LOCALTZ)
        self.creation_date = creation_date #: Creation date of the template
        if revision_date is None:
            revision_date = datetime.now(LOCALTZ)
        elif isinstance(revision_date, datetime) and not revision_date.tzinfo:
            revision_date = revision_date.replace(tzinfo=LOCALTZ)
        self.revision_date = revision_date #: Last revision date of the catalog
        self.fuzzy = fuzzy #: Catalog header fuzzy bit (`True` or `False`)

        self.obsolete = odict() #: Dictionary of obsolete messages
        self._num_plurals = None
        self._plural_expr = None

    def _get_header_comment(self):
        comment = self._header_comment
        comment = comment.replace('PROJECT', self.project) \
                         .replace('VERSION', self.version) \
                         .replace('YEAR', self.revision_date.strftime('%Y')) \
                         .replace('ORGANIZATION', self.copyright_holder)
        if self.locale:
            comment = comment.replace('Translations template', '%s translations'
                                      % self.locale.english_name)
        return comment

    def _set_header_comment(self, string):
        self._header_comment = string

    header_comment = property(_get_header_comment, _set_header_comment, doc="""\
    The header comment for the catalog.

    >>> catalog = Catalog(project='Foobar', version='1.0',
    ...                   copyright_holder='Foo Company')
    >>> print catalog.header_comment #doctest: +ELLIPSIS
    # Translations template for Foobar.
    # Copyright (C) ... Foo Company
    # This file is distributed under the same license as the Foobar project.
    # FIRST AUTHOR <EMAIL@ADDRESS>, ....
    #

    The header can also be set from a string. Any known upper-case variables
    will be replaced when the header is retrieved again:

    >>> catalog = Catalog(project='Foobar', version='1.0',
    ...                   copyright_holder='Foo Company')
    >>> catalog.header_comment = '''\\
    ... # The POT for my really cool PROJECT project.
    ... # Copyright (C) 1990-2003 ORGANIZATION
    ... # This file is distributed under the same license as the PROJECT
    ... # project.
    ... #'''
    >>> print catalog.header_comment
    # The POT for my really cool Foobar project.
    # Copyright (C) 1990-2003 Foo Company
    # This file is distributed under the same license as the Foobar
    # project.
    #

    :type: `unicode`
    """)

    def _get_mime_headers(self):
        headers = []
        headers.append(('Project-Id-Version',
                        '%s %s' % (self.project, self.version)))
        headers.append(('Report-Msgid-Bugs-To', self.msgid_bugs_address))
        headers.append(('POT-Creation-Date',
                        format_datetime(self.creation_date, 'yyyy-MM-dd HH:mmZ',
                                        locale='en')))
        if self.locale is None:
            headers.append(('PO-Revision-Date', 'YEAR-MO-DA HO:MI+ZONE'))
            headers.append(('Last-Translator', 'FULL NAME <EMAIL@ADDRESS>'))
            headers.append(('Language-Team', 'LANGUAGE <LL@li.org>'))
        else:
            headers.append(('PO-Revision-Date',
                            format_datetime(self.revision_date,
                                            'yyyy-MM-dd HH:mmZ', locale='en')))
            headers.append(('Last-Translator', self.last_translator))
            headers.append(('Language-Team',
                           self.language_team.replace('LANGUAGE',
                                                      str(self.locale))))
            headers.append(('Plural-Forms', self.plural_forms))
        headers.append(('MIME-Version', '1.0'))
        headers.append(('Content-Type',
                        'text/plain; charset=%s' % self.charset))
        headers.append(('Content-Transfer-Encoding', '8bit'))
        headers.append(('Generated-By', 'Babel %s\n' % VERSION))
        return headers

    def _set_mime_headers(self, headers):
        for name, value in headers:
            if name.lower() == 'content-type':
                mimetype, params = parse_header(value)
                if 'charset' in params:
                    self.charset = params['charset'].lower()
                break
        for name, value in headers:
            name = name.lower().decode(self.charset)
            value = value.decode(self.charset)
            if name == 'project-id-version':
                parts = value.split(' ')
                self.project = u' '.join(parts[:-1])
                self.version = parts[-1]
            elif name == 'report-msgid-bugs-to':
                self.msgid_bugs_address = value
            elif name == 'last-translator':
                self.last_translator = value
            elif name == 'language-team':
                self.language_team = value
            elif name == 'plural-forms':
                _, params = parse_header(' ;' + value)
                self._num_plurals = int(params.get('nplurals', 2))
                self._plural_expr = params.get('plural', '(n != 1)')
            elif name == 'pot-creation-date':
                # FIXME: this should use dates.parse_datetime as soon as that
                #        is ready
                value, tzoffset, _ = re.split('([+-]\d{4})$', value, 1)

                tt = time.strptime(value, '%Y-%m-%d %H:%M')
                ts = time.mktime(tt)

                # Separate the offset into a sign component, hours, and minutes
                plus_minus_s, rest = tzoffset[0], tzoffset[1:]
                hours_offset_s, mins_offset_s = rest[:2], rest[2:]

                # Make them all integers
                plus_minus = int(plus_minus_s + '1')
                hours_offset = int(hours_offset_s)
                mins_offset = int(mins_offset_s)

                # Calculate net offset
                net_mins_offset = hours_offset * 60
                net_mins_offset += mins_offset
                net_mins_offset *= plus_minus

                # Create an offset object
                tzoffset = FixedOffsetTimezone(net_mins_offset)

                # Store the offset in a datetime object
                dt = datetime.fromtimestamp(ts)
                self.creation_date = dt.replace(tzinfo=tzoffset)
            elif name == 'po-revision-date':
                # Keep the value if it's not the default one
                if 'YEAR' not in value:
                    # FIXME: this should use dates.parse_datetime as soon as
                    #        that is ready
                    value, tzoffset, _ = re.split('([+-]\d{4})$', value, 1)
                    tt = time.strptime(value, '%Y-%m-%d %H:%M')
                    ts = time.mktime(tt)

                    # Separate the offset into a sign component, hours, and
                    # minutes
                    plus_minus_s, rest = tzoffset[0], tzoffset[1:]
                    hours_offset_s, mins_offset_s = rest[:2], rest[2:]

                    # Make them all integers
                    plus_minus = int(plus_minus_s + '1')
                    hours_offset = int(hours_offset_s)
                    mins_offset = int(mins_offset_s)

                    # Calculate net offset
                    net_mins_offset = hours_offset * 60
                    net_mins_offset += mins_offset
                    net_mins_offset *= plus_minus

                    # Create an offset object
                    tzoffset = FixedOffsetTimezone(net_mins_offset)

                    # Store the offset in a datetime object
                    dt = datetime.fromtimestamp(ts)
                    self.revision_date = dt.replace(tzinfo=tzoffset)

    mime_headers = property(_get_mime_headers, _set_mime_headers, doc="""\
    The MIME headers of the catalog, used for the special ``msgid ""`` entry.

    The behavior of this property changes slightly depending on whether a locale
    is set or not, the latter indicating that the catalog is actually a template
    for actual translations.

    Here's an example of the output for such a catalog template:

    >>> created = datetime(1990, 4, 1, 15, 30, tzinfo=UTC)
    >>> catalog = Catalog(project='Foobar', version='1.0',
    ...                   creation_date=created)
    >>> for name, value in catalog.mime_headers:
    ...     print '%s: %s' % (name, value)
    Project-Id-Version: Foobar 1.0
    Report-Msgid-Bugs-To: EMAIL@ADDRESS
    POT-Creation-Date: 1990-04-01 15:30+0000
    PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE
    Last-Translator: FULL NAME <EMAIL@ADDRESS>
    Language-Team: LANGUAGE <LL@li.org>
    MIME-Version: 1.0
    Content-Type: text/plain; charset=utf-8
    Content-Transfer-Encoding: 8bit
    Generated-By: Babel ...

    And here's an example of the output when the locale is set:

    >>> revised = datetime(1990, 8, 3, 12, 0, tzinfo=UTC)
    >>> catalog = Catalog(locale='de_DE', project='Foobar', version='1.0',
    ...                   creation_date=created, revision_date=revised,
    ...                   last_translator='John Doe <jd@example.com>',
    ...                   language_team='de_DE <de@example.com>')
    >>> for name, value in catalog.mime_headers:
    ...     print '%s: %s' % (name, value)
    Project-Id-Version: Foobar 1.0
    Report-Msgid-Bugs-To: EMAIL@ADDRESS
    POT-Creation-Date: 1990-04-01 15:30+0000
    PO-Revision-Date: 1990-08-03 12:00+0000
    Last-Translator: John Doe <jd@example.com>
    Language-Team: de_DE <de@example.com>
    Plural-Forms: nplurals=2; plural=(n != 1)
    MIME-Version: 1.0
    Content-Type: text/plain; charset=utf-8
    Content-Transfer-Encoding: 8bit
    Generated-By: Babel ...

    :type: `list`
    """)

    def num_plurals(self):
        if self._num_plurals is None:
            num = 2
            if self.locale:
                num = get_plural(self.locale)[0]
            self._num_plurals = num
        return self._num_plurals
    num_plurals = property(num_plurals, doc="""\
    The number of plurals used by the catalog or locale.

    >>> Catalog(locale='en').num_plurals
    2
    >>> Catalog(locale='ga').num_plurals
    3

    :type: `int`
    """)

    def plural_expr(self):
        if self._plural_expr is None:
            expr = '(n != 1)'
            if self.locale:
                expr = get_plural(self.locale)[1]
            self._plural_expr = expr
        return self._plural_expr
    plural_expr = property(plural_expr, doc="""\
    The plural expression used by the catalog or locale.

    >>> Catalog(locale='en').plural_expr
    '(n != 1)'
    >>> Catalog(locale='ga').plural_expr
    '(n==1 ? 0 : n==2 ? 1 : 2)'

    :type: `basestring`
    """)

    def plural_forms(self):
        return 'nplurals=%s; plural=%s' % (self.num_plurals, self.plural_expr)
    plural_forms = property(plural_forms, doc="""\
    Return the plural forms declaration for the locale.

    >>> Catalog(locale='en').plural_forms
    'nplurals=2; plural=(n != 1)'
    >>> Catalog(locale='pt_BR').plural_forms
    'nplurals=2; plural=(n > 1)'

    :type: `str`
    """)

    def __contains__(self, id):
        """Return whether the catalog has a message with the specified ID."""
        return self._key_for(id) in self._messages

    def __len__(self):
        """The number of messages in the catalog.

        This does not include the special ``msgid ""`` entry.
        """
        return len(self._messages)

    def __iter__(self):
        """Iterates through all the entries in the catalog, in the order they
        were added, yielding a `Message` object for every entry.

        :rtype: ``iterator``
        """
        buf = []
        for name, value in self.mime_headers:
            buf.append('%s: %s' % (name, value))
        flags = set()
        if self.fuzzy:
            flags |= set(['fuzzy'])
        yield Message(u'', '\n'.join(buf), flags=flags)
        for key in self._messages:
            yield self._messages[key]

    def __repr__(self):
        locale = ''
        if self.locale:
            locale = ' %s' % self.locale
        return '<%s %r%s>' % (type(self).__name__, self.domain, locale)

    def __delitem__(self, id):
        """Delete the message with the specified ID."""
        key = self._key_for(id)
        if key in self._messages:
            del self._messages[key]

    def __getitem__(self, id):
        """Return the message with the specified ID.

        :param id: the message ID
        :return: the message with the specified ID, or `None` if no such message
                 is in the catalog
        :rtype: `Message`
        """
        return self._messages.get(self._key_for(id))

    def __setitem__(self, id, message):
        """Add or update the message with the specified ID.

        >>> catalog = Catalog()
        >>> catalog[u'foo'] = Message(u'foo')
        >>> catalog[u'foo']
        <Message u'foo' (flags: [])>

        If a message with that ID is already in the catalog, it is updated
        to include the locations and flags of the new message.

        >>> catalog = Catalog()
        >>> catalog[u'foo'] = Message(u'foo', locations=[('main.py', 1)])
        >>> catalog[u'foo'].locations
        [('main.py', 1)]
        >>> catalog[u'foo'] = Message(u'foo', locations=[('utils.py', 5)])
        >>> catalog[u'foo'].locations
        [('main.py', 1), ('utils.py', 5)]

        :param id: the message ID
        :param message: the `Message` object
        """
        assert isinstance(message, Message), 'expected a Message object'
        key = self._key_for(id)
        current = self._messages.get(key)
        if current:
            if message.pluralizable and not current.pluralizable:
                # The new message adds pluralization
                current.id = message.id
                current.string = message.string
            current.locations = list(distinct(current.locations +
                                              message.locations))
            current.auto_comments = list(distinct(current.auto_comments +
                                                  message.auto_comments))
            current.user_comments = list(distinct(current.user_comments +
                                                  message.user_comments))
            current.flags |= message.flags
            message = current
        elif id == '':
            # special treatment for the header message
            headers = message_from_string(message.string.encode(self.charset))
            self.mime_headers = headers.items()
            self.header_comment = '\n'.join(['# %s' % comment for comment
                                             in message.user_comments])
            self.fuzzy = message.fuzzy
        else:
            if isinstance(id, (list, tuple)):
                assert isinstance(message.string, (list, tuple)), \
                    'Expected sequence but got %s' % type(message.string)
            self._messages[key] = message

    def add(self, id, string=None, locations=(), flags=(), auto_comments=(),
            user_comments=(), previous_id=(), lineno=None):
        """Add or update the message with the specified ID.

        >>> catalog = Catalog()
        >>> catalog.add(u'foo')
        >>> catalog[u'foo']
        <Message u'foo' (flags: [])>

        This method simply constructs a `Message` object with the given
        arguments and invokes `__setitem__` with that object.

        :param id: the message ID, or a ``(singular, plural)`` tuple for
                   pluralizable messages
        :param string: the translated message string, or a
                       ``(singular, plural)`` tuple for pluralizable messages
        :param locations: a sequence of ``(filenname, lineno)`` tuples
        :param flags: a set or sequence of flags
        :param auto_comments: a sequence of automatic comments
        :param user_comments: a sequence of user comments
        :param previous_id: the previous message ID, or a ``(singular, plural)``
                            tuple for pluralizable messages
        :param lineno: the line number on which the msgid line was found in the
                       PO file, if any
        """
        self[id] = Message(id, string, list(locations), flags, auto_comments,
                           user_comments, previous_id, lineno=lineno)

    def check(self):
        """Run various validation checks on the translations in the catalog.

        For every message which fails validation, this method yield a
        ``(message, errors)`` tuple, where ``message`` is the `Message` object
        and ``errors`` is a sequence of `TranslationError` objects.

        :rtype: ``iterator``
        """
        for message in self._messages.values():
            errors = message.check(catalog=self)
            if errors:
                yield message, errors

    def update(self, template, no_fuzzy_matching=False):
        """Update the catalog based on the given template catalog.

        >>> from babel.messages import Catalog
        >>> template = Catalog()
        >>> template.add('green', locations=[('main.py', 99)])
        >>> template.add('blue', locations=[('main.py', 100)])
        >>> template.add(('salad', 'salads'), locations=[('util.py', 42)])
        >>> catalog = Catalog(locale='de_DE')
        >>> catalog.add('blue', u'blau', locations=[('main.py', 98)])
        >>> catalog.add('head', u'Kopf', locations=[('util.py', 33)])
        >>> catalog.add(('salad', 'salads'), (u'Salat', u'Salate'),
        ...             locations=[('util.py', 38)])

        >>> catalog.update(template)
        >>> len(catalog)
        3

        >>> msg1 = catalog['green']
        >>> msg1.string
        >>> msg1.locations
        [('main.py', 99)]

        >>> msg2 = catalog['blue']
        >>> msg2.string
        u'blau'
        >>> msg2.locations
        [('main.py', 100)]

        >>> msg3 = catalog['salad']
        >>> msg3.string
        (u'Salat', u'Salate')
        >>> msg3.locations
        [('util.py', 42)]

        Messages that are in the catalog but not in the template are removed
        from the main collection, but can still be accessed via the `obsolete`
        member:

        >>> 'head' in catalog
        False
        >>> catalog.obsolete.values()
        [<Message 'head' (flags: [])>]

        :param template: the reference catalog, usually read from a POT file
        :param no_fuzzy_matching: whether to use fuzzy matching of message IDs
        """
        messages = self._messages
        remaining = messages.copy()
        self._messages = odict()

        # Prepare for fuzzy matching
        fuzzy_candidates = []
        if not no_fuzzy_matching:
            fuzzy_candidates = [
                self._key_for(msgid) for msgid in messages
                if msgid and messages[msgid].string
            ]
        fuzzy_matches = set()

        def _merge(message, oldkey, newkey):
            message = message.clone()
            fuzzy = False
            if oldkey != newkey:
                fuzzy = True
                fuzzy_matches.add(oldkey)
                oldmsg = messages.get(oldkey)
                if isinstance(oldmsg.id, basestring):
                    message.previous_id = [oldmsg.id]
                else:
                    message.previous_id = list(oldmsg.id)
            else:
                oldmsg = remaining.pop(oldkey, None)
            message.string = oldmsg.string
            if isinstance(message.id, (list, tuple)):
                if not isinstance(message.string, (list, tuple)):
                    fuzzy = True
                    message.string = tuple(
                        [message.string] + ([u''] * (len(message.id) - 1))
                    )
                elif len(message.string) != self.num_plurals:
                    fuzzy = True
                    message.string = tuple(message.string[:len(oldmsg.string)])
            elif isinstance(message.string, (list, tuple)):
                fuzzy = True
                message.string = message.string[0]
            message.flags |= oldmsg.flags
            if fuzzy:
                message.flags |= set([u'fuzzy'])
            self[message.id] = message

        for message in template:
            if message.id:
                key = self._key_for(message.id)
                if key in messages:
                    _merge(message, key, key)
                else:
                    if no_fuzzy_matching is False:
                        # do some fuzzy matching with difflib
                        matches = get_close_matches(key.lower().strip(),
                                                    fuzzy_candidates, 1)
                        if matches:
                            _merge(message, matches[0], key)
                            continue

                    self[message.id] = message

        self.obsolete = odict()
        for msgid in remaining:
            if no_fuzzy_matching or msgid not in fuzzy_matches:
                self.obsolete[msgid] = remaining[msgid]
        # Make updated catalog's POT-Creation-Date equal to the template
        # used to update the catalog
        self.creation_date = template.creation_date

    def _key_for(self, id):
        """The key for a message is just the singular ID even for pluralizable
        messages.
        """
        key = id
        if isinstance(key, (list, tuple)):
            key = id[0]
        return key
