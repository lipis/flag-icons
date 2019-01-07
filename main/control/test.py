# coding: utf-8

import flask
import flask_wtf
import wtforms

import auth
import util
import versions

from main import app


TESTS = [
  'alert',
  'badge',
  'button',
  'filter',
  'font',
  'form',
  'grid',
  'heading',
  'label',
  'pageres',
  'pagination',
  'paragraph',
  'responsive',
  'social',
  'table',
  'versions',
]


class TestForm(flask_wtf.FlaskForm):
  name = wtforms.StringField(
    'Text',
    [wtforms.validators.required()], filters=[util.strip_filter],
    description='This is a very important field',
  )
  number = wtforms.IntegerField('Integer', [wtforms.validators.optional()])
  email = wtforms.StringField(
    'Email',
    [wtforms.validators.optional(), wtforms.validators.email()],
    filters=[util.email_filter],
  )
  date = wtforms.DateField('Date', [wtforms.validators.optional()])
  textarea = wtforms.TextAreaField('Textarea')
  boolean = wtforms.BooleanField(
    'Render it as Markdown',
    [wtforms.validators.optional()],
  )
  password = wtforms.PasswordField(
    'Password',
    [wtforms.validators.optional(), wtforms.validators.length(min=6)],
  )
  password_visible = wtforms.StringField(
    'Password visible',
    [wtforms.validators.optional(), wtforms.validators.length(min=6)],
    description='Visible passwords for the win!'
  )
  prefix = wtforms.StringField('Prefix', [wtforms.validators.optional()])
  suffix = wtforms.StringField('Suffix', [wtforms.validators.required()])
  both = wtforms.IntegerField('Both', [wtforms.validators.required()])
  select = wtforms.SelectField(
    'Language',
    [wtforms.validators.optional()],
    choices=[(s, s.title()) for s in ['english', 'greek', 'spanish']]
  )
  checkboxes = wtforms.SelectMultipleField(
    'User permissions',
    [wtforms.validators.required()],
    choices=[(c, c.title()) for c in ['admin', 'moderator', 'slave']]
  )
  radios = wtforms.SelectField(
    'Choose your weapon',
    [wtforms.validators.optional()],
    choices=[(r, r.title()) for r in ['gun', 'knife', 'chainsaw', 'sword']]
  )
  public = wtforms.StringField('Public Key', [wtforms.validators.optional()])
  private = wtforms.StringField('Private Key', [wtforms.validators.optional()])
  recaptcha = flask_wtf.RecaptchaField()


@app.route('/admin/test/<test>/', methods=['GET', 'POST'])
@app.route('/admin/test/', methods=['GET', 'POST'])
@auth.admin_required
def admin_test(test=None):
  if test and test not in TESTS:
    flask.abort(404)
  form = TestForm()
  if form.validate_on_submit():
    pass

  return flask.render_template(
    'admin/test/test_one.html' if test else 'admin/test/test.html',
    title='Test: %s' % test.title() if test else 'Test',
    html_class='test',
    form=form,
    test=test,
    tests=TESTS,
    versions=versions.get_versions(),
    back_url_for='admin_test' if test else None,
  )
