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

"""Core locale representation and locale data access."""

import os
import pickle

from babel import localedata

__all__ = ['UnknownLocaleError', 'Locale', 'default_locale', 'negotiate_locale',
           'parse_locale']
__docformat__ = 'restructuredtext en'

_global_data = None

def get_global(key):
    """Return the dictionary for the given key in the global data.
    
    The global data is stored in the ``babel/global.dat`` file and contains
    information independent of individual locales.
    
    >>> get_global('zone_aliases')['UTC']
    'Etc/GMT'
    >>> get_global('zone_territories')['Europe/Berlin']
    'DE'
    
    :param key: the data key
    :return: the dictionary found in the global data under the given key
    :rtype: `dict`
    :since: version 0.9
    """
    global _global_data
    if _global_data is None:
        dirname = os.path.join(os.path.dirname(__file__))
        filename = os.path.join(dirname, 'global.dat')
        fileobj = open(filename, 'rb')
        try:
            _global_data = pickle.load(fileobj)
        finally:
            fileobj.close()
    return _global_data.get(key, {})


LOCALE_ALIASES = {
    'ar': 'ar_SY', 'bg': 'bg_BG', 'bs': 'bs_BA', 'ca': 'ca_ES', 'cs': 'cs_CZ', 
    'da': 'da_DK', 'de': 'de_DE', 'el': 'el_GR', 'en': 'en_US', 'es': 'es_ES', 
    'et': 'et_EE', 'fa': 'fa_IR', 'fi': 'fi_FI', 'fr': 'fr_FR', 'gl': 'gl_ES', 
    'he': 'he_IL', 'hu': 'hu_HU', 'id': 'id_ID', 'is': 'is_IS', 'it': 'it_IT', 
    'ja': 'ja_JP', 'km': 'km_KH', 'ko': 'ko_KR', 'lt': 'lt_LT', 'lv': 'lv_LV', 
    'mk': 'mk_MK', 'nl': 'nl_NL', 'nn': 'nn_NO', 'no': 'nb_NO', 'pl': 'pl_PL', 
    'pt': 'pt_PT', 'ro': 'ro_RO', 'ru': 'ru_RU', 'sk': 'sk_SK', 'sl': 'sl_SI', 
    'sv': 'sv_SE', 'th': 'th_TH', 'tr': 'tr_TR', 'uk': 'uk_UA'
}


class UnknownLocaleError(Exception):
    """Exception thrown when a locale is requested for which no locale data
    is available.
    """

    def __init__(self, identifier):
        """Create the exception.
        
        :param identifier: the identifier string of the unsupported locale
        """
        Exception.__init__(self, 'unknown locale %r' % identifier)
        self.identifier = identifier


class Locale(object):
    """Representation of a specific locale.
    
    >>> locale = Locale('en', 'US')
    >>> repr(locale)
    '<Locale "en_US">'
    >>> locale.display_name
    u'English (United States)'
    
    A `Locale` object can also be instantiated from a raw locale string:
    
    >>> locale = Locale.parse('en-US', sep='-')
    >>> repr(locale)
    '<Locale "en_US">'
    
    `Locale` objects provide access to a collection of locale data, such as
    territory and language names, number and date format patterns, and more:
    
    >>> locale.number_symbols['decimal']
    u'.'
    
    If a locale is requested for which no locale data is available, an
    `UnknownLocaleError` is raised:
    
    >>> Locale.parse('en_DE')
    Traceback (most recent call last):
        ...
    UnknownLocaleError: unknown locale 'en_DE'
    
    :see: `IETF RFC 3066 <http://www.ietf.org/rfc/rfc3066.txt>`_
    """

    def __init__(self, language, territory=None, script=None, variant=None):
        """Initialize the locale object from the given identifier components.
        
        >>> locale = Locale('en', 'US')
        >>> locale.language
        'en'
        >>> locale.territory
        'US'
        
        :param language: the language code
        :param territory: the territory (country or region) code
        :param script: the script code
        :param variant: the variant code
        :raise `UnknownLocaleError`: if no locale data is available for the
                                     requested locale
        """
        self.language = language
        self.territory = territory
        self.script = script
        self.variant = variant
        self.__data = None

        identifier = str(self)
        if not localedata.exists(identifier):
            raise UnknownLocaleError(identifier)

    def default(cls, category=None, aliases=LOCALE_ALIASES):
        """Return the system default locale for the specified category.
        
        >>> for name in ['LANGUAGE', 'LC_ALL', 'LC_CTYPE']:
        ...     os.environ[name] = ''
        >>> os.environ['LANG'] = 'fr_FR.UTF-8'
        >>> Locale.default('LC_MESSAGES')
        <Locale "fr_FR">

        :param category: one of the ``LC_XXX`` environment variable names
        :param aliases: a dictionary of aliases for locale identifiers
        :return: the value of the variable, or any of the fallbacks
                 (``LANGUAGE``, ``LC_ALL``, ``LC_CTYPE``, and ``LANG``)
        :rtype: `Locale`
        :see: `default_locale`
        """
        return cls(default_locale(category, aliases=aliases))
    default = classmethod(default)

    def negotiate(cls, preferred, available, sep='_', aliases=LOCALE_ALIASES):
        """Find the best match between available and requested locale strings.
        
        >>> Locale.negotiate(['de_DE', 'en_US'], ['de_DE', 'de_AT'])
        <Locale "de_DE">
        >>> Locale.negotiate(['de_DE', 'en_US'], ['en', 'de'])
        <Locale "de">
        >>> Locale.negotiate(['de_DE', 'de'], ['en_US'])
        
        You can specify the character used in the locale identifiers to separate
        the differnet components. This separator is applied to both lists. Also,
        case is ignored in the comparison:
        
        >>> Locale.negotiate(['de-DE', 'de'], ['en-us', 'de-de'], sep='-')
        <Locale "de_DE">
        
        :param preferred: the list of locale identifers preferred by the user
        :param available: the list of locale identifiers available
        :param aliases: a dictionary of aliases for locale identifiers
        :return: the `Locale` object for the best match, or `None` if no match
                 was found
        :rtype: `Locale`
        :see: `negotiate_locale`
        """
        identifier = negotiate_locale(preferred, available, sep=sep,
                                      aliases=aliases)
        if identifier:
            return Locale.parse(identifier, sep=sep)
    negotiate = classmethod(negotiate)

    def parse(cls, identifier, sep='_'):
        """Create a `Locale` instance for the given locale identifier.
        
        >>> l = Locale.parse('de-DE', sep='-')
        >>> l.display_name
        u'Deutsch (Deutschland)'
        
        If the `identifier` parameter is not a string, but actually a `Locale`
        object, that object is returned:
        
        >>> Locale.parse(l)
        <Locale "de_DE">
        
        :param identifier: the locale identifier string
        :param sep: optional component separator
        :return: a corresponding `Locale` instance
        :rtype: `Locale`
        :raise `ValueError`: if the string does not appear to be a valid locale
                             identifier
        :raise `UnknownLocaleError`: if no locale data is available for the
                                     requested locale
        :see: `parse_locale`
        """
        if isinstance(identifier, basestring):
            return cls(*parse_locale(identifier, sep=sep))
        return identifier
    parse = classmethod(parse)

    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '<Locale "%s">' % str(self)

    def __str__(self):
        return '_'.join(filter(None, [self.language, self.script,
                                      self.territory, self.variant]))

    def _data(self):
        if self.__data is None:
            self.__data = localedata.LocaleDataDict(localedata.load(str(self)))
        return self.__data
    _data = property(_data)

    def get_display_name(self, locale=None):
        """Return the display name of the locale using the given locale.
        
        The display name will include the language, territory, script, and
        variant, if those are specified.
        
        >>> Locale('zh', 'CN', script='Hans').get_display_name('en')
        u'Chinese (Simplified Han, China)'
        
        :param locale: the locale to use
        :return: the display name
        """
        if locale is None:
            locale = self
        locale = Locale.parse(locale)
        retval = locale.languages.get(self.language)
        if self.territory or self.script or self.variant:
            details = []
            if self.script:
                details.append(locale.scripts.get(self.script))
            if self.territory:
                details.append(locale.territories.get(self.territory))
            if self.variant:
                details.append(locale.variants.get(self.variant))
            details = filter(None, details)
            if details:
                retval += ' (%s)' % u', '.join(details)
        return retval

    display_name = property(get_display_name, doc="""\
        The localized display name of the locale.
        
        >>> Locale('en').display_name
        u'English'
        >>> Locale('en', 'US').display_name
        u'English (United States)'
        >>> Locale('sv').display_name
        u'svenska'
        
        :type: `unicode`
        """)

    def english_name(self):
        return self.get_display_name(Locale('en'))
    english_name = property(english_name, doc="""\
        The english display name of the locale.
        
        >>> Locale('de').english_name
        u'German'
        >>> Locale('de', 'DE').english_name
        u'German (Germany)'
        
        :type: `unicode`
        """)

    #{ General Locale Display Names

    def languages(self):
        return self._data['languages']
    languages = property(languages, doc="""\
        Mapping of language codes to translated language names.
        
        >>> Locale('de', 'DE').languages['ja']
        u'Japanisch'
        
        :type: `dict`
        :see: `ISO 639 <http://www.loc.gov/standards/iso639-2/>`_
        """)

    def scripts(self):
        return self._data['scripts']
    scripts = property(scripts, doc="""\
        Mapping of script codes to translated script names.
        
        >>> Locale('en', 'US').scripts['Hira']
        u'Hiragana'
        
        :type: `dict`
        :see: `ISO 15924 <http://www.evertype.com/standards/iso15924/>`_
        """)

    def territories(self):
        return self._data['territories']
    territories = property(territories, doc="""\
        Mapping of script codes to translated script names.
        
        >>> Locale('es', 'CO').territories['DE']
        u'Alemania'
        
        :type: `dict`
        :see: `ISO 3166 <http://www.iso.org/iso/en/prods-services/iso3166ma/>`_
        """)

    def variants(self):
        return self._data['variants']
    variants = property(variants, doc="""\
        Mapping of script codes to translated script names.
        
        >>> Locale('de', 'DE').variants['1901']
        u'Alte deutsche Rechtschreibung'
        
        :type: `dict`
        """)

    #{ Number Formatting

    def currencies(self):
        return self._data['currency_names']
    currencies = property(currencies, doc="""\
        Mapping of currency codes to translated currency names.
        
        >>> Locale('en').currencies['COP']
        u'Colombian Peso'
        >>> Locale('de', 'DE').currencies['COP']
        u'Kolumbianischer Peso'
        
        :type: `dict`
        """)

    def currency_symbols(self):
        return self._data['currency_symbols']
    currency_symbols = property(currency_symbols, doc="""\
        Mapping of currency codes to symbols.
        
        >>> Locale('en', 'US').currency_symbols['USD']
        u'$'
        >>> Locale('es', 'CO').currency_symbols['USD']
        u'US$'
        
        :type: `dict`
        """)

    def number_symbols(self):
        return self._data['number_symbols']
    number_symbols = property(number_symbols, doc="""\
        Symbols used in number formatting.
        
        >>> Locale('fr', 'FR').number_symbols['decimal']
        u','
        
        :type: `dict`
        """)

    def decimal_formats(self):
        return self._data['decimal_formats']
    decimal_formats = property(decimal_formats, doc="""\
        Locale patterns for decimal number formatting.
        
        >>> Locale('en', 'US').decimal_formats[None]
        <NumberPattern u'#,##0.###'>
        
        :type: `dict`
        """)

    def currency_formats(self):
        return self._data['currency_formats']
    currency_formats = property(currency_formats, doc=r"""\
        Locale patterns for currency number formatting.
        
        >>> print Locale('en', 'US').currency_formats[None]
        <NumberPattern u'\xa4#,##0.00'>
        
        :type: `dict`
        """)

    def percent_formats(self):
        return self._data['percent_formats']
    percent_formats = property(percent_formats, doc="""\
        Locale patterns for percent number formatting.
        
        >>> Locale('en', 'US').percent_formats[None]
        <NumberPattern u'#,##0%'>
        
        :type: `dict`
        """)

    def scientific_formats(self):
        return self._data['scientific_formats']
    scientific_formats = property(scientific_formats, doc="""\
        Locale patterns for scientific number formatting.
        
        >>> Locale('en', 'US').scientific_formats[None]
        <NumberPattern u'#E0'>
        
        :type: `dict`
        """)

    #{ Calendar Information and Date Formatting

    def periods(self):
        return self._data['periods']
    periods = property(periods, doc="""\
        Locale display names for day periods (AM/PM).
        
        >>> Locale('en', 'US').periods['am']
        u'AM'
        
        :type: `dict`
        """)

    def days(self):
        return self._data['days']
    days = property(days, doc="""\
        Locale display names for weekdays.
        
        >>> Locale('de', 'DE').days['format']['wide'][3]
        u'Donnerstag'
        
        :type: `dict`
        """)

    def months(self):
        return self._data['months']
    months = property(months, doc="""\
        Locale display names for months.
        
        >>> Locale('de', 'DE').months['format']['wide'][10]
        u'Oktober'
        
        :type: `dict`
        """)

    def quarters(self):
        return self._data['quarters']
    quarters = property(quarters, doc="""\
        Locale display names for quarters.
        
        >>> Locale('de', 'DE').quarters['format']['wide'][1]
        u'1. Quartal'
        
        :type: `dict`
        """)

    def eras(self):
        return self._data['eras']
    eras = property(eras, doc="""\
        Locale display names for eras.
        
        >>> Locale('en', 'US').eras['wide'][1]
        u'Anno Domini'
        >>> Locale('en', 'US').eras['abbreviated'][0]
        u'BC'
        
        :type: `dict`
        """)

    def time_zones(self):
        return self._data['time_zones']
    time_zones = property(time_zones, doc="""\
        Locale display names for time zones.
        
        >>> Locale('en', 'US').time_zones['Europe/London']['long']['daylight']
        u'British Summer Time'
        >>> Locale('en', 'US').time_zones['America/St_Johns']['city']
        u"St. John's"
        
        :type: `dict`
        """)

    def meta_zones(self):
        return self._data['meta_zones']
    meta_zones = property(meta_zones, doc="""\
        Locale display names for meta time zones.
        
        Meta time zones are basically groups of different Olson time zones that
        have the same GMT offset and daylight savings time.
        
        >>> Locale('en', 'US').meta_zones['Europe_Central']['long']['daylight']
        u'Central European Summer Time'
        
        :type: `dict`
        :since: version 0.9
        """)

    def zone_formats(self):
        return self._data['zone_formats']
    zone_formats = property(zone_formats, doc=r"""\
        Patterns related to the formatting of time zones.
        
        >>> Locale('en', 'US').zone_formats['fallback']
        u'%(1)s (%(0)s)'
        >>> Locale('pt', 'BR').zone_formats['region']
        u'Hor\xe1rio %s'
        
        :type: `dict`
        :since: version 0.9
        """)

    def first_week_day(self):
        return self._data['week_data']['first_day']
    first_week_day = property(first_week_day, doc="""\
        The first day of a week, with 0 being Monday.
        
        >>> Locale('de', 'DE').first_week_day
        0
        >>> Locale('en', 'US').first_week_day
        6
        
        :type: `int`
        """)

    def weekend_start(self):
        return self._data['week_data']['weekend_start']
    weekend_start = property(weekend_start, doc="""\
        The day the weekend starts, with 0 being Monday.
        
        >>> Locale('de', 'DE').weekend_start
        5
        
        :type: `int`
        """)

    def weekend_end(self):
        return self._data['week_data']['weekend_end']
    weekend_end = property(weekend_end, doc="""\
        The day the weekend ends, with 0 being Monday.
        
        >>> Locale('de', 'DE').weekend_end
        6
        
        :type: `int`
        """)

    def min_week_days(self):
        return self._data['week_data']['min_days']
    min_week_days = property(min_week_days, doc="""\
        The minimum number of days in a week so that the week is counted as the
        first week of a year or month.
        
        >>> Locale('de', 'DE').min_week_days
        4
        
        :type: `int`
        """)

    def date_formats(self):
        return self._data['date_formats']
    date_formats = property(date_formats, doc="""\
        Locale patterns for date formatting.
        
        >>> Locale('en', 'US').date_formats['short']
        <DateTimePattern u'M/d/yy'>
        >>> Locale('fr', 'FR').date_formats['long']
        <DateTimePattern u'd MMMM yyyy'>
        
        :type: `dict`
        """)

    def time_formats(self):
        return self._data['time_formats']
    time_formats = property(time_formats, doc="""\
        Locale patterns for time formatting.
        
        >>> Locale('en', 'US').time_formats['short']
        <DateTimePattern u'h:mm a'>
        >>> Locale('fr', 'FR').time_formats['long']
        <DateTimePattern u'HH:mm:ss z'>
        
        :type: `dict`
        """)

    def datetime_formats(self):
        return self._data['datetime_formats']
    datetime_formats = property(datetime_formats, doc="""\
        Locale patterns for datetime formatting.
        
        >>> Locale('en').datetime_formats[None]
        u'{1} {0}'
        >>> Locale('th').datetime_formats[None]
        u'{1}, {0}'
        
        :type: `dict`
        """)


def default_locale(category=None, aliases=LOCALE_ALIASES):
    """Returns the system default locale for a given category, based on
    environment variables.
    
    >>> for name in ['LANGUAGE', 'LC_ALL', 'LC_CTYPE']:
    ...     os.environ[name] = ''
    >>> os.environ['LANG'] = 'fr_FR.UTF-8'
    >>> default_locale('LC_MESSAGES')
    'fr_FR'

    The "C" or "POSIX" pseudo-locales are treated as aliases for the
    "en_US_POSIX" locale:

    >>> os.environ['LC_MESSAGES'] = 'POSIX'
    >>> default_locale('LC_MESSAGES')
    'en_US_POSIX'

    :param category: one of the ``LC_XXX`` environment variable names
    :param aliases: a dictionary of aliases for locale identifiers
    :return: the value of the variable, or any of the fallbacks (``LANGUAGE``,
             ``LC_ALL``, ``LC_CTYPE``, and ``LANG``)
    :rtype: `str`
    """
    varnames = (category, 'LANGUAGE', 'LC_ALL', 'LC_CTYPE', 'LANG')
    for name in filter(None, varnames):
        locale = os.getenv(name)
        if locale:
            if name == 'LANGUAGE' and ':' in locale:
                # the LANGUAGE variable may contain a colon-separated list of
                # language codes; we just pick the language on the list
                locale = locale.split(':')[0]
            if locale in ('C', 'POSIX'):
                locale = 'en_US_POSIX'
            elif aliases and locale in aliases:
                locale = aliases[locale]
            try:
                return '_'.join(filter(None, parse_locale(locale)))
            except ValueError:
                pass

def negotiate_locale(preferred, available, sep='_', aliases=LOCALE_ALIASES):
    """Find the best match between available and requested locale strings.
    
    >>> negotiate_locale(['de_DE', 'en_US'], ['de_DE', 'de_AT'])
    'de_DE'
    >>> negotiate_locale(['de_DE', 'en_US'], ['en', 'de'])
    'de'
    
    Case is ignored by the algorithm, the result uses the case of the preferred
    locale identifier:
    
    >>> negotiate_locale(['de_DE', 'en_US'], ['de_de', 'de_at'])
    'de_DE'
    
    >>> negotiate_locale(['de_DE', 'en_US'], ['de_de', 'de_at'])
    'de_DE'
    
    By default, some web browsers unfortunately do not include the territory
    in the locale identifier for many locales, and some don't even allow the
    user to easily add the territory. So while you may prefer using qualified
    locale identifiers in your web-application, they would not normally match
    the language-only locale sent by such browsers. To workaround that, this
    function uses a default mapping of commonly used langauge-only locale
    identifiers to identifiers including the territory:
    
    >>> negotiate_locale(['ja', 'en_US'], ['ja_JP', 'en_US'])
    'ja_JP'
    
    Some browsers even use an incorrect or outdated language code, such as "no"
    for Norwegian, where the correct locale identifier would actually be "nb_NO"
    (Bokmål) or "nn_NO" (Nynorsk). The aliases are intended to take care of
    such cases, too:
    
    >>> negotiate_locale(['no', 'sv'], ['nb_NO', 'sv_SE'])
    'nb_NO'
    
    You can override this default mapping by passing a different `aliases`
    dictionary to this function, or you can bypass the behavior althogher by
    setting the `aliases` parameter to `None`.
    
    :param preferred: the list of locale strings preferred by the user
    :param available: the list of locale strings available
    :param sep: character that separates the different parts of the locale
                strings
    :param aliases: a dictionary of aliases for locale identifiers
    :return: the locale identifier for the best match, or `None` if no match
             was found
    :rtype: `str`
    """
    available = [a.lower() for a in available if a]
    for locale in preferred:
        ll = locale.lower()
        if ll in available:
            return locale
        if aliases:
            alias = aliases.get(ll)
            if alias:
                alias = alias.replace('_', sep)
                if alias.lower() in available:
                    return alias
        parts = locale.split(sep)
        if len(parts) > 1 and parts[0].lower() in available:
            return parts[0]
    return None

def parse_locale(identifier, sep='_'):
    """Parse a locale identifier into a tuple of the form::
    
      ``(language, territory, script, variant)``
    
    >>> parse_locale('zh_CN')
    ('zh', 'CN', None, None)
    >>> parse_locale('zh_Hans_CN')
    ('zh', 'CN', 'Hans', None)
    
    The default component separator is "_", but a different separator can be
    specified using the `sep` parameter:
    
    >>> parse_locale('zh-CN', sep='-')
    ('zh', 'CN', None, None)
    
    If the identifier cannot be parsed into a locale, a `ValueError` exception
    is raised:
    
    >>> parse_locale('not_a_LOCALE_String')
    Traceback (most recent call last):
      ...
    ValueError: 'not_a_LOCALE_String' is not a valid locale identifier
    
    Encoding information and locale modifiers are removed from the identifier:
    
    >>> parse_locale('it_IT@euro')
    ('it', 'IT', None, None)
    >>> parse_locale('en_US.UTF-8')
    ('en', 'US', None, None)
    >>> parse_locale('de_DE.iso885915@euro')
    ('de', 'DE', None, None)
    
    :param identifier: the locale identifier string
    :param sep: character that separates the different components of the locale
                identifier
    :return: the ``(language, territory, script, variant)`` tuple
    :rtype: `tuple`
    :raise `ValueError`: if the string does not appear to be a valid locale
                         identifier
    
    :see: `IETF RFC 4646 <http://www.ietf.org/rfc/rfc4646.txt>`_
    """
    if '.' in identifier:
        # this is probably the charset/encoding, which we don't care about
        identifier = identifier.split('.', 1)[0]
    if '@' in identifier:
        # this is a locale modifier such as @euro, which we don't care about
        # either
        identifier = identifier.split('@', 1)[0]

    parts = identifier.split(sep)
    lang = parts.pop(0).lower()
    if not lang.isalpha():
        raise ValueError('expected only letters, got %r' % lang)

    script = territory = variant = None
    if parts:
        if len(parts[0]) == 4 and parts[0].isalpha():
            script = parts.pop(0).title()

    if parts:
        if len(parts[0]) == 2 and parts[0].isalpha():
            territory = parts.pop(0).upper()
        elif len(parts[0]) == 3 and parts[0].isdigit():
            territory = parts.pop(0)

    if parts:
        if len(parts[0]) == 4 and parts[0][0].isdigit() or \
                len(parts[0]) >= 5 and parts[0][0].isalpha():
            variant = parts.pop()

    if parts:
        raise ValueError('%r is not a valid locale identifier' % identifier)

    return lang, territory, script, variant
