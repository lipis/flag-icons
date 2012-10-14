import decimal

from wtforms import fields, widgets

class ReferencePropertyField(fields.SelectFieldBase):
    """
    A field for ``db.ReferenceProperty``. The list items are rendered in a
    select.

    :param reference_class:
        A db.Model class which will be used to generate the default query
        to make the list of items. If this is not specified, The `query`
        property must be overridden before validation.
    :param label_attr:
        If specified, use this attribute on the model class as the label
        associated with each option. Otherwise, the model object's
        `__str__` or `__unicode__` will be used.
    :param allow_blank:
        If set to true, a blank choice will be added to the top of the list
        to allow `None` to be chosen.
    :param blank_text:
        Use this to override the default blank option's label.
    """
    widget = widgets.Select()

    def __init__(self, label=None, validators=None, reference_class=None,
                 label_attr=None, allow_blank=False, blank_text=u'', **kwargs):
        super(ReferencePropertyField, self).__init__(label, validators,
                                                     **kwargs)
        self.label_attr = label_attr
        self.allow_blank = allow_blank
        self.blank_text = blank_text
        self._set_data(None)
        if reference_class is not None:
            self.query = reference_class.all()

    def _get_data(self):
        if self._formdata is not None:
            for obj in self.query:
                if str(obj.key()) == self._formdata:
                    self._set_data(obj)
                    break
        return self._data

    def _set_data(self, data):
        self._data = data
        self._formdata = None

    data = property(_get_data, _set_data)

    def iter_choices(self):
        if self.allow_blank:
            yield (u'__None', self.blank_text, self.data is None)

        for obj in self.query:
            key = str(obj.key())
            label = self.label_attr and getattr(obj, self.label_attr) or obj
            yield (key, label, self.data and ( self.data.key( ) == obj.key() ) )

    def process_formdata(self, valuelist):
        if valuelist:
            if valuelist[0] == '__None':
                self.data = None
            else:
                self._data = None
                self._formdata = valuelist[0]

    def pre_validate(self, form):
        if not self.allow_blank or self.data is not None:
            for obj in self.query:
                if str(self.data.key()) == str(obj.key()):
                    break
            else:
                raise ValueError(self.gettext(u'Not a valid choice'))


class StringListPropertyField(fields.TextAreaField):
    """
    A field for ``db.StringListProperty``. The list items are rendered in a
    textarea.
    """
    def _value(self):
        if self.raw_data:
            return self.raw_data[0]
        else:
            return self.data and unicode("\n".join(self.data)) or u''

    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = valuelist[0].splitlines()
            except ValueError:
                raise ValueError(self.gettext(u'Not a valid list'))


class GeoPtPropertyField(fields.TextField):

    def process_formdata(self, valuelist):
        if valuelist:
            try:
                lat, lon = valuelist[0].split(',')
                self.data = u'%s,%s' % (decimal.Decimal(lat.strip()), decimal.Decimal(lon.strip()),)
            except (decimal.InvalidOperation, ValueError):
                raise ValueError(u'Not a valid coordinate location')
