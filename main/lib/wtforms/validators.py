import re


__all__ = (
    'Email', 'email', 'EqualTo', 'equal_to', 'IPAddress', 'ip_address',
    'Length', 'length', 'NumberRange', 'number_range', 'Optional', 'optional',
    'Required', 'required', 'Regexp', 'regexp', 'URL', 'url', 'AnyOf',
    'any_of', 'NoneOf', 'none_of'
)


class ValidationError(ValueError):
    """
    Raised when a validator fails to validate its input.
    """
    def __init__(self, message=u'', *args, **kwargs):
        ValueError.__init__(self, message, *args, **kwargs)


class StopValidation(Exception):
    """
    Causes the validation chain to stop.

    If StopValidation is raised, no more validators in the validation chain are
    called. If raised with a message, the message will be added to the errors
    list.
    """
    def __init__(self, message=u'', *args, **kwargs):
        Exception.__init__(self, message, *args, **kwargs)


class EqualTo(object):
    """
    Compares the values of two fields.

    :param fieldname:
        The name of the other field to compare to.
    :param message:
        Error message to raise in case of a validation error. Can be
        interpolated with `%(other_label)s` and `%(other_name)s` to provide a
        more helpful error.
    """
    def __init__(self, fieldname, message=None):
        self.fieldname = fieldname
        self.message = message

    def __call__(self, form, field):
        try:
            other = form[self.fieldname]
        except KeyError:
            raise ValidationError(field.gettext(u"Invalid field name '%s'.") % self.fieldname)
        if field.data != other.data:
            d = {
                'other_label': hasattr(other, 'label') and other.label.text or self.fieldname,
                'other_name': self.fieldname
            }
            if self.message is None:
                self.message = field.gettext(u'Field must be equal to %(other_name)s.')

            raise ValidationError(self.message % d)


class Length(object):
    """
    Validates the length of a string.

    :param min:
        The minimum required length of the string. If not provided, minimum
        length will not be checked.
    :param max:
        The maximum length of the string. If not provided, maximum length
        will not be checked.
    :param message:
        Error message to raise in case of a validation error. Can be
        interpolated using `%(min)d` and `%(max)d` if desired. Useful defaults
        are provided depending on the existence of min and max.
    """
    def __init__(self, min=-1, max=-1, message=None):
        assert min != -1 or max!=-1, 'At least one of `min` or `max` must be specified.'
        assert max == -1 or min <= max, '`min` cannot be more than `max`.'
        self.min = min
        self.max = max
        self.message = message

    def __call__(self, form, field):
        l = field.data and len(field.data) or 0
        if l < self.min or self.max != -1 and l > self.max:
            if self.message is None:
                if self.max == -1:
                    self.message = field.ngettext(u'Field must be at least %(min)d character long.',
                                                  u'Field must be at least %(min)d characters long.', self.min)
                elif self.min == -1:
                    self.message = field.ngettext(u'Field cannot be longer than %(max)d character.',
                                                  u'Field cannot be longer than %(max)d characters.', self.max)
                else:
                    self.message = field.gettext(u'Field must be between %(min)d and %(max)d characters long.')

            raise ValidationError(self.message % dict(min=self.min, max=self.max))


class NumberRange(object):
    """
    Validates that a number is of a minimum and/or maximum value, inclusive.
    This will work with any comparable number type, such as floats and
    decimals, not just integers.

    :param min:
        The minimum required value of the number. If not provided, minimum
        value will not be checked.
    :param max:
        The maximum value of the number. If not provided, maximum value
        will not be checked.
    :param message:
        Error message to raise in case of a validation error. Can be
        interpolated using `%(min)s` and `%(max)s` if desired. Useful defaults
        are provided depending on the existence of min and max.
    """
    def __init__(self, min=None, max=None, message=None):
        self.min = min
        self.max = max
        self.message = message

    def __call__(self, form, field):
        data = field.data
        if data is None or (self.min is not None and data < self.min) or \
            (self.max is not None and data > self.max):
            if self.message is None:
                # we use %(min)s interpolation to support floats, None, and
                # Decimals without throwing a formatting exception.
                if self.max is None:
                    self.message = field.gettext(u'Number must be greater than %(min)s.')
                elif self.min is None:
                    self.message = field.gettext(u'Number must be less than %(max)s.')
                else:
                    self.message = field.gettext(u'Number must be between %(min)s and %(max)s.')

            raise ValidationError(self.message % dict(min=self.min, max=self.max))


class Optional(object):
    """
    Allows empty input and stops the validation chain from continuing.

    If input is empty, also removes prior errors (such as processing errors)
    from the field.
    """
    field_flags = ('optional', )

    def __call__(self, form, field):
        if not field.raw_data or isinstance(field.raw_data[0], basestring) and not field.raw_data[0].strip():
            field.errors[:] = []
            raise StopValidation()


class Required(object):
    """
    Validates that the field contains data. This validator will stop the
    validation chain on error.

    :param message:
        Error message to raise in case of a validation error.
    """
    field_flags = ('required', )

    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        if not field.data or isinstance(field.data, basestring) and not field.data.strip():
            if self.message is None:
                self.message = field.gettext(u'This field is required.')

            field.errors[:] = []
            raise StopValidation(self.message)


class Regexp(object):
    """
    Validates the field against a user provided regexp.

    :param regex:
        The regular expression string to use. Can also be a compiled regular
        expression pattern.
    :param flags:
        The regexp flags to use, for example re.IGNORECASE. Ignored if
        `regex` is not a string.
    :param message:
        Error message to raise in case of a validation error.
    """
    def __init__(self, regex, flags=0, message=None):
        if isinstance(regex, basestring):
            regex = re.compile(regex, flags)
        self.regex = regex
        self.message = message

    def __call__(self, form, field):
        if not self.regex.match(field.data or u''):
            if self.message is None:
                self.message = field.gettext(u'Invalid input.')

            raise ValidationError(self.message)


class Email(Regexp):
    """
    Validates an email address. Note that this uses a very primitive regular
    expression and should only be used in instances where you later verify by
    other means, such as email activation or lookups.

    :param message:
        Error message to raise in case of a validation error.
    """
    def __init__(self, message=None):
        super(Email, self).__init__(r'^.+@[^.].*\.[a-z]{2,10}$', re.IGNORECASE, message)

    def __call__(self, form, field):
        if self.message is None:
            self.message = field.gettext(u'Invalid email address.')

        super(Email, self).__call__(form, field)


class IPAddress(Regexp):
    """
    Validates an IP(v4) address.

    :param message:
        Error message to raise in case of a validation error.
    """
    def __init__(self, message=None):
        super(IPAddress, self).__init__(r'^([0-9]{1,3}\.){3}[0-9]{1,3}$', message=message)

    def __call__(self, form, field):
        if self.message is None:
            self.message = field.gettext(u'Invalid IP address.')

        super(IPAddress, self).__call__(form, field)


class URL(Regexp):
    """
    Simple regexp based url validation. Much like the email validator, you
    probably want to validate the url later by other means if the url must
    resolve.

    :param require_tld:
        If true, then the domain-name portion of the URL must contain a .tld
        suffix.  Set this to false if you want to allow domains like
        `localhost`.
    :param message:
        Error message to raise in case of a validation error.
    """
    def __init__(self, require_tld=True, message=None):
        tld_part = (require_tld and ur'\.[a-z]{2,10}' or u'')
        regex = ur'^[a-z]+://([^/:]+%s|([0-9]{1,3}\.){3}[0-9]{1,3})(:[0-9]+)?(\/.*)?$' % tld_part
        super(URL, self).__init__(regex, re.IGNORECASE, message)

    def __call__(self, form, field):
        if self.message is None:
            self.message = field.gettext(u'Invalid URL.')

        super(URL, self).__call__(form, field)


class AnyOf(object):
    """
    Compares the incoming data to a sequence of valid inputs.

    :param values:
        A sequence of valid inputs.
    :param message:
        Error message to raise in case of a validation error. `%(values)s`
        contains the list of values.
    :param values_formatter:
        Function used to format the list of values in the error message.
    """
    def __init__(self, values, message=None, values_formatter=None):
        self.values = values
        self.message = message
        if values_formatter is None:
            values_formatter = lambda v: u', '.join(v)
        self.values_formatter = values_formatter

    def __call__(self, form, field):
        if field.data not in self.values:
            if self.message is None:
                self.message = field.gettext(u'Invalid value, must be one of: %(values)s.')

            raise ValueError(self.message % dict(values=self.values_formatter(self.values)))


class NoneOf(object):
    """
    Compares the incoming data to a sequence of invalid inputs.

    :param values:
        A sequence of invalid inputs.
    :param message:
        Error message to raise in case of a validation error. `%(values)s`
        contains the list of values.
    :param values_formatter:
        Function used to format the list of values in the error message.
    """
    def __init__(self, values, message=None, values_formatter=None):
        self.values = values
        self.message = message
        if values_formatter is None:
            values_formatter = lambda v: u', '.join(v)
        self.values_formatter = values_formatter

    def __call__(self, form, field):
        if field.data in self.values:
            if self.message is None:
                self.message = field.gettext(u'Invalid value, can\'t be any of: %(values)s.')

            raise ValueError(self.message % dict(values=self.values_formatter(self.values)))


email = Email
equal_to = EqualTo
ip_address = IPAddress
length = Length
number_range = NumberRange
optional = Optional
required = Required
regexp = Regexp
url = URL
any_of = AnyOf
none_of = NoneOf
