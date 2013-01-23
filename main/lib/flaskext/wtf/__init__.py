# -*- coding: utf-8 -*-
"""
    flask.ext.wtf
    ~~~~~~~~~~~~

    Flask-WTF extension

    :copyright: (c) 2010 by Dan Jacob.
    :license: BSD, see LICENSE for more details.
"""

try:
    import sqlalchemy
    _is_sqlalchemy = True
except ImportError:
    _is_sqlalchemy = False

from wtforms import fields, widgets, validators
from wtforms.fields import *
from wtforms.validators import *
from wtforms.widgets import *
from wtforms import ValidationError

from . import html5
from .form import Form
from . import recaptcha

from .recaptcha.fields import RecaptchaField
from .recaptcha.widgets import RecaptchaWidget
from .recaptcha.validators import Recaptcha

fields.RecaptchaField = RecaptchaField
widgets.RecaptchaWidget = RecaptchaWidget
validators.Recaptcha = Recaptcha

from .file import FileField
from .file import FileAllowed, FileRequired, file_allowed, file_required

fields.FileField = FileField

validators.file_allowed = file_allowed
validators.file_required = file_required
validators.FileAllowed = FileAllowed
validators.FileRequired = FileRequired


__all__ = ['Form', 'ValidationError', 'fields', 'validators', 'widgets', 'html5']

__all__ += [str(v) for v in validators.__all__ ]
__all__ += [str(v) for v in (fields.__all__ if hasattr(fields, '__all__') else
    fields.core.__all__) ]

__all__ += [str(v) for v in (widgets.__all__ if hasattr(widgets, '__all__') else
    widgets.core.__all__)]
__all__ += recaptcha.__all__

if _is_sqlalchemy:
    from wtforms.ext.sqlalchemy.fields import QuerySelectField, \
        QuerySelectMultipleField

    __all__ += ['QuerySelectField',
                'QuerySelectMultipleField']

    for field in (QuerySelectField,
                  QuerySelectMultipleField):

        setattr(fields, field.__name__, field)
