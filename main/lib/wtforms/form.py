import sys

__all__ = (
    'BaseForm',
    'Form',
)

from wtforms.compat import with_metaclass, iteritems, itervalues

class BaseForm(object):
    """
    Base Form Class.  Provides core behaviour like field construction,
    validation, and data and error proxying.
    """

    def __init__(self, fields, prefix=''):
        """
        :param fields:
            A dict or sequence of 2-tuples of partially-constructed fields.
        :param prefix:
            If provided, all fields will have their name prefixed with the
            value.
        """
        if prefix and prefix[-1] not in '-_;:/.':
            prefix += '-'

        self._prefix = prefix
        self._errors = None
        self._fields = {}

        if hasattr(fields, 'iteritems'):
            fields = fields.iteritems()
        elif hasattr(fields, 'items'):
            fields = fields.items()

        translations = self._get_translations()

        for name, unbound_field in fields:
            field = unbound_field.bind(form=self, name=name, prefix=prefix, translations=translations)
            self._fields[name] = field

    def __iter__(self):
        """ Iterate form fields in arbitrary order """
        return iter(itervalues(self._fields))

    def __contains__(self, name):
        """ Returns `True` if the named field is a member of this form. """
        return (name in self._fields)

    def __getitem__(self, name):
        """ Dict-style access to this form's fields."""
        return self._fields[name]

    def __setitem__(self, name, value):
        """ Bind a field to this form. """
        self._fields[name] = value.bind(form=self, name=name, prefix=self._prefix)

    def __delitem__(self, name):
        """ Remove a field from this form. """
        del self._fields[name]

    def _get_translations(self):
        """
        Override in subclasses to provide alternate translations factory.

        Must return an object that provides gettext() and ngettext() methods.
        """
        return None

    def populate_obj(self, obj):
        """
        Populates the attributes of the passed `obj` with data from the form's
        fields.

        :note: This is a destructive operation; Any attribute with the same name
               as a field will be overridden. Use with caution.
        """
        for name, field in iteritems(self._fields):
            field.populate_obj(obj, name)

    def process(self, formdata=None, obj=None, **kwargs):
        """
        Take form, object data, and keyword arg input and have the fields
        process them.

        :param formdata:
            Used to pass data coming from the enduser, usually `request.POST` or
            equivalent.
        :param obj:
            If `formdata` is empty or not provided, this object is checked for
            attributes matching form field names, which will be used for field
            values.
        :param `**kwargs`:
            If `formdata` is empty or not provided and `obj` does not contain
            an attribute named the same as a field, form will assign the value
            of a matching keyword argument to the field, if one exists.
        """
        if formdata is not None and not hasattr(formdata, 'getlist'):
            if hasattr(formdata, 'getall'):
                formdata = WebobInputWrapper(formdata)
            else:
                raise TypeError("formdata should be a multidict-type wrapper that supports the 'getlist' method")

        for name, field, in iteritems(self._fields):
            if obj is not None and hasattr(obj, name):
                field.process(formdata, getattr(obj, name))
            elif name in kwargs:
                field.process(formdata, kwargs[name])
            else:
                field.process(formdata)

    def validate(self, extra_validators=None):
        """
        Validates the form by calling `validate` on each field.

        :param extra_validators:
            If provided, is a dict mapping field names to a sequence of
            callables which will be passed as extra validators to the field's
            `validate` method.

        Returns `True` if no errors occur.
        """
        self._errors = None
        success = True
        for name, field in iteritems(self._fields):
            if extra_validators is not None and name in extra_validators:
                extra = extra_validators[name]
            else:
                extra = tuple()
            if not field.validate(self, extra):
                success = False
        return success

    @property
    def data(self):
        return dict((name, f.data) for name, f in iteritems(self._fields))

    @property
    def errors(self):
        if self._errors is None:
            self._errors = dict((name, f.errors) for name, f in iteritems(self._fields) if f.errors)
        return self._errors


class FormMeta(type):
    """
    The metaclass for `Form` and any subclasses of `Form`.

    `FormMeta`'s responsibility is to create the `_unbound_fields` list, which
    is a list of `UnboundField` instances sorted by their order of
    instantiation.  The list is created at the first instantiation of the form.
    If any fields are added/removed from the form, the list is cleared to be
    re-generated on the next instantiaton.

    Any properties which begin with an underscore or are not `UnboundField`
    instances are ignored by the metaclass.
    """
    def __init__(cls, name, bases, attrs):
        type.__init__(cls, name, bases, attrs)
        cls._unbound_fields = None

    def __call__(cls, *args, **kwargs):
        """
        Construct a new `Form` instance, creating `_unbound_fields` on the
        class if it is empty.
        """
        if cls._unbound_fields is None:
            fields = []
            for name in dir(cls):
                if not name.startswith('_'):
                    unbound_field = getattr(cls, name)
                    if hasattr(unbound_field, '_formfield'):
                        fields.append((name, unbound_field))
            # We keep the name as the second element of the sort
            # to ensure a stable sort.
            fields.sort(key=lambda x: (x[1].creation_counter, x[0]))
            cls._unbound_fields = fields
        return type.__call__(cls, *args, **kwargs)

    def __setattr__(cls, name, value):
        """
        Add an attribute to the class, clearing `_unbound_fields` if needed.
        """
        if not name.startswith('_') and hasattr(value, '_formfield'):
            cls._unbound_fields = None
        type.__setattr__(cls, name, value)

    def __delattr__(cls, name):
        """
        Remove an attribute from the class, clearing `_unbound_fields` if
        needed.
        """
        if not name.startswith('_'):
            cls._unbound_fields = None
        type.__delattr__(cls, name)


class Form(with_metaclass(FormMeta, BaseForm)):
    """
    Declarative Form base class. Extends BaseForm's core behaviour allowing
    fields to be defined on Form subclasses as class attributes.

    In addition, form and instance input data are taken at construction time
    and passed to `process()`.
    """

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        """
        :param formdata:
            Used to pass data coming from the enduser, usually `request.POST` or
            equivalent.
        :param obj:
            If `formdata` is empty or not provided, this object is checked for
            attributes matching form field names, which will be used for field
            values.
        :param prefix:
            If provided, all fields will have their name prefixed with the
            value.
        :param `**kwargs`:
            If `formdata` is empty or not provided and `obj` does not contain
            an attribute named the same as a field, form will assign the value
            of a matching keyword argument to the field, if one exists.
        """
        super(Form, self).__init__(self._unbound_fields, prefix=prefix)

        for name, field in iteritems(self._fields):
            # Set all the fields to attributes so that they obscure the class
            # attributes with the same names.
            setattr(self, name, field)

        self.process(formdata, obj, **kwargs)

    def __iter__(self):
        """ Iterate form fields in their order of definition on the form. """
        for name, _ in self._unbound_fields:
            if name in self._fields:
                yield self._fields[name]

    def __setitem__(self, name, value):
        raise TypeError('Fields may not be added to Form instances, only classes.')

    def __delitem__(self, name):
        del self._fields[name]
        setattr(self, name, None)

    def __delattr__(self, name):
        try:
            self.__delitem__(name)
        except KeyError:
            super(Form, self).__delattr__(name)

    def validate(self):
        """
        Validates the form by calling `validate` on each field, passing any
        extra `Form.validate_<fieldname>` validators to the field validator.
        """
        extra = {}
        for name in self._fields:
            inline = getattr(self.__class__, 'validate_%s' % name, None)
            if inline is not None:
                extra[name] = [inline]

        return super(Form, self).validate(extra)


class WebobInputWrapper(object):
    """
    Wrap a webob MultiDict for use as passing as `formdata` to Field.

    Since for consistency, we have decided in WTForms to support as input a
    small subset of the API provided in common between cgi.FieldStorage,
    Django's QueryDict, and Werkzeug's MultiDict, we need to wrap Webob, the
    only supported framework whose multidict does not fit this API, but is
    nevertheless used by a lot of frameworks.

    While we could write a full wrapper to support all the methods, this will
    undoubtedly result in bugs due to some subtle differences between the
    various wrappers. So we will keep it simple.
    """

    def __init__(self, multidict):
        self._wrapped = multidict

    def __iter__(self):
        return iter(self._wrapped)

    def __len__(self):
        return len(self._wrapped)

    def __contains__(self, name):
        return (name in self._wrapped)

    def getlist(self, name):
        return self._wrapped.getall(name)

