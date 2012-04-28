# -*- coding: utf-8 -*-
"""
    flaskext.wtf
    ~~~~~~~~~~~~

    Flask-WTF extension

    :copyright: (c) 2010 by Dan Jacob.
    :license: BSD, see LICENSE for more details.
"""

import warnings
import uuid

from wtforms.fields import BooleanField, DecimalField, DateField, \
    DateTimeField, FieldList, FloatField, FormField, \
    HiddenField, IntegerField, PasswordField, RadioField, SelectField, \
    SelectMultipleField, SubmitField, TextField, TextAreaField

from wtforms.validators import Email, email, EqualTo, equal_to, \
    IPAddress, ip_address, Length, length, NumberRange, number_range, \
    Optional, optional, Required, required, Regexp, regexp, \
    URL, url, AnyOf, any_of, NoneOf, none_of

from wtforms.widgets import CheckboxInput, FileInput, HiddenInput, \
    ListWidget, PasswordInput, RadioInput, Select, SubmitInput, \
    TableWidget, TextArea, TextInput

from wtforms.fields import FileField as _FileField

try:
    import sqlalchemy
    _is_sqlalchemy = True
except ImportError:
    _is_sqlalchemy = False


from wtforms import Form as BaseForm
from wtforms import fields, widgets, validators, ValidationError

from flask import request, session, current_app

from jinja2 import Markup

from flaskext.wtf import html5

from flaskext.wtf import recaptcha

from flaskext.wtf.recaptcha.fields import RecaptchaField
from flaskext.wtf.recaptcha.widgets import RecaptchaWidget
from flaskext.wtf.recaptcha.validators import Recaptcha

fields.RecaptchaField = RecaptchaField
widgets.RecaptchaWidget = RecaptchaWidget
validators.Recaptcha = Recaptcha

from flaskext.wtf.file import FileField
from flaskext.wtf.file import FileAllowed, FileRequired, file_allowed, \
        file_required

fields.FileField = FileField

validators.file_allowed = file_allowed
validators.file_required = file_required
validators.FileAllowed = FileAllowed
validators.FileRequired = FileRequired


__all__  = ['Form', 'ValidationError',
            'fields', 'validators', 'widgets', 'html5']

__all__ += fields.__all__
__all__ += validators.__all__
__all__ += widgets.__all__
__all__ += recaptcha.__all__

if _is_sqlalchemy:
    from wtforms.ext.sqlalchemy.fields import QuerySelectField, \
        QuerySelectMultipleField

    __all__ += ['QuerySelectField', 
                'QuerySelectMultipleField']

    for field in (QuerySelectField, 
                  QuerySelectMultipleField):

        setattr(fields, field.__name__, field)


def _generate_csrf_token():
    return str(uuid.uuid4())


class Form(BaseForm):

    """
    Subclass of WTForms **Form** class. The main difference is that
    **request.form** is passed as `formdata` argument to constructor
    so can handle request data implicitly. 

    In addition this **Form** implementation has automatic CSRF handling.
    """

    csrf = fields.HiddenField()

    def __init__(self, formdata=None, *args, **kwargs):

        csrf_enabled = kwargs.pop('csrf_enabled', None)

        if csrf_enabled is None:
            csrf_enabled = current_app.config.get('CSRF_ENABLED', True)
        
        self.csrf_enabled = csrf_enabled

        self.csrf_session_key = kwargs.pop('csrf_session_key', None)

        if self.csrf_session_key is None:
            self.csrf_session_key = \
                current_app.config.get('CSRF_SESSION_KEY', '_csrf_token')

        csrf_token = session.get(self.csrf_session_key, None)

        if csrf_token is None:
            csrf_token = self.reset_csrf()

        super(Form, self).__init__(formdata, csrf=csrf_token, *args, **kwargs)

    def is_submitted(self):
        """
        Checks if form has been submitted. The default case is if the HTTP 
        method is **PUT** or **POST**.
        """

        return request and request.method in ("PUT", "POST")

    def process(self, formdata=None, obj=None, **kwargs):

        if self.is_submitted():
        
            if formdata is None:
                formdata = request.form

            # ensure csrf validation occurs ONLY when formdata is passed
            # in case "csrf" is the only field in the form

            if not formdata and not request.files:
                self.csrf_is_valid = False
            else:
                self.csrf_is_valid = None

        super(Form, self).process(formdata, obj, **kwargs)

    @property
    def csrf_token(self):
        """
        Renders CSRF field inside a hidden DIV.

        :deprecated: Use **hidden_tag** instead.
        """
        warnings.warn("csrf_token is deprecated. Use hidden_tag instead", 
                      DeprecationWarning)

        return self.hidden_tag('csrf')

    def reset_csrf(self):
        """
        Resets the CSRF token in the session. If you are reusing the form
        in the same view (i.e. you are not redirecting somewhere else)
        it's recommended you call this before rendering the form.
        """
        
        csrf_token = _generate_csrf_token()
        session[self.csrf_session_key] = csrf_token
        return csrf_token

    def validate_csrf(self, field):
        if not self.csrf_enabled:
            return

        csrf_token = session.pop(self.csrf_session_key, None)
        is_valid = field.data and \
                   field.data == csrf_token and \
                   self.csrf_is_valid is not False

        # reset this field, otherwise stale token is displayed
        field.data = self.reset_csrf()

        # we set this flag to ensure consistent behaviour when
        # calling validate() more than once

        self.csrf_is_valid = bool(is_valid)

        if not is_valid:
            raise ValidationError, "Missing or invalid CSRF token"

    def hidden_tag(self, *fields):
        """
        Wraps hidden fields in a hidden DIV tag, in order to keep XHTML 
        compliance.

        .. versionadded:: 0.3

        :param fields: list of hidden field names. If not provided will render
                       all hidden fields, including the CSRF field.
        """

        if not fields:
            fields = [f for f in self if isinstance(f, HiddenField)]

        rv = [u'<div style="display:none;">']
        for field in fields:
            if isinstance(field, basestring):
                field = getattr(self, field)
            rv.append(unicode(field))
        rv.append(u"</div>")

        return Markup(u"".join(rv))
        
    def validate_on_submit(self):
        """
        Checks if form has been submitted and if so runs validate. This is 
        a shortcut, equivalent to ``form.is_submitted() and form.validate()``
        """
        return self.is_submitted() and self.validate()
    

