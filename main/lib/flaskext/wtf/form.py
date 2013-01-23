import werkzeug.datastructures

from jinja2 import Markup
from flask import request, session, current_app
from wtforms.fields import HiddenField
from wtforms.ext.csrf.session import SessionSecureForm

class _Auto():
    '''Placeholder for unspecified variables that should be set to defaults.

    Used when None is a valid option and should not be replaced by a default.
    '''
    pass

class Form(SessionSecureForm):

    """
    Flask-specific subclass of WTForms **SessionSecureForm** class.

    Flask-specific behaviors:
    If formdata is not specified, this will use flask.request.form. Explicitly
      pass formdata = None to prevent this.

    csrf_context - a session or dict-like object to use when making CSRF tokens.
      Default: flask.session.

    secret_key - a secret key for building CSRF tokens. If this isn't specified,
      the form will take the first of these that is defined:
        * the SECRET_KEY attribute on this class
        * the value of flask.current_app.config["SECRET_KEY"]
        * the session's secret_key
      If none of these are set, raise an exception.

    csrf_enabled - whether to use CSRF protection. If False, all csrf behavior
      is suppressed. Default: check app.config for CSRF_ENABLED, else True

    """
    def __init__(self, formdata=_Auto, obj=None, prefix='', csrf_context=None,
                 secret_key=None, csrf_enabled=None, *args, **kwargs):

        if csrf_enabled is None:
            csrf_enabled = current_app.config.get('CSRF_ENABLED', True)
        self.csrf_enabled = csrf_enabled

        if formdata is _Auto:
            if self.is_submitted():
                formdata = request.form
                if request.files:
                    formdata = formdata.copy()
                    formdata.update(request.files)
                elif request.json:
                    formdata = werkzeug.datastructures.MultiDict(request.json);
            else:
                formdata = None
        if self.csrf_enabled:
            if csrf_context is None:
                csrf_context = session
            if secret_key is None:
                # It wasn't passed in, check if the class has a SECRET_KEY set
                secret_key = getattr(self, "SECRET_KEY", None)
            if secret_key is None:
                # It wasn't on the class, check the application config
                secret_key = current_app.config.get("SECRET_KEY")
            if secret_key is None and session:
                # It's not there either! Is there a session secret key if we can
                secret_key = session.secret_key
            if secret_key is None:
                # It wasn't anywhere. This is an error.
                raise Exception('Must provide secret_key to use csrf.')

            self.SECRET_KEY = secret_key
        else:
            csrf_context = {}
            self.SECRET_KEY = ""
        super(Form, self).__init__(formdata, obj, prefix, csrf_context=csrf_context, *args, **kwargs)

    def generate_csrf_token(self, csrf_context=None):
        if not self.csrf_enabled:
            return None
        return super(Form, self).generate_csrf_token(csrf_context)

    def validate_csrf_token(self, field):
        if not self.csrf_enabled:
            return
        super(Form, self).validate_csrf_token(field)

    def is_submitted(self):
        """
        Checks if form has been submitted. The default case is if the HTTP 
        method is **PUT** or **POST**.
        """

        return request and request.method in ("PUT", "POST")

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
    
