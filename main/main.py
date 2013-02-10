import sys
sys.path.insert(0, 'lib.zip')

import flask
from flaskext import wtf
import config

app = flask.Flask(__name__)
app.config.from_object(config)
app.jinja_env.line_statement_prefix = '#'

from google.appengine.api import mail

import auth
import util
import model
import admin


@app.route('/')
def welcome():
  return flask.render_template(
      'welcome.html',
      html_class='welcome',
    )


################################################################################
# Profile stuff
################################################################################
class ProfileUpdateForm(wtf.Form):
  name = wtf.TextField('Name', [wtf.validators.required()])
  email = wtf.TextField('Email', [
      wtf.validators.optional(),
      wtf.validators.email('That does not look like an email'),
    ])


@app.route('/_s/profile/', endpoint='profile_service')
@app.route('/profile/', methods=['GET', 'POST'], endpoint='profile')
@auth.login_required
def profile():
  form = ProfileUpdateForm()
  user_db = auth.current_user_db()
  if form.validate_on_submit():
    user_db.name = form.name.data
    user_db.email = form.email.data.lower()
    user_db.put()
    return flask.redirect(flask.url_for('welcome'))
  if not form.errors:
    form.name.data = user_db.name
    form.email.data = user_db.email or ''

  if flask.request.path.startswith('/_s/'):
    return util.jsonify_model_db(user_db)

  return flask.render_template(
      'profile.html',
      title='Profile',
      html_class='profile',
      form=form,
      user_db=user_db,
    )


################################################################################
# Feedback
################################################################################
class FeedbackForm(wtf.Form):
  subject = wtf.TextField('Subject', [wtf.validators.required()])
  message = wtf.TextAreaField('Message', [wtf.validators.required()])
  email = wtf.TextField('Email (optional)', [
      wtf.validators.optional(),
      wtf.validators.email('That does not look like an email'),
    ])


@app.route('/feedback/', methods=['GET', 'POST'])
def feedback():
  form = FeedbackForm()
  if form.validate_on_submit():
    mail.send_mail(
        sender=config.CONFIG_DB.feedback_email,
        to=config.CONFIG_DB.feedback_email,
        subject='[%s] %s' % (
            config.CONFIG_DB.brand_name,
            form.subject.data,
          ),
        reply_to=form.email.data or config.CONFIG_DB.feedback_email,
        body='%s\n\n%s' % (form.message.data, form.email.data)
      )
    flask.flash('Thank you for your feedback!', category='success')
    return flask.redirect(flask.url_for('welcome'))
  if not form.errors and auth.current_user_id() > 0:
    form.email.data = auth.current_user_db().email

  return flask.render_template(
      'feedback.html',
      title='Feedback',
      html_class='feedback',
      form=form,
    )


################################################################################
# User Stuff
################################################################################
@app.route('/_s/user/', endpoint='user_list_service')
@app.route('/user/', endpoint='user_list')
@auth.admin_required
def user_list():
  user_dbs, more_cursor = util.retrieve_dbs(
      model.User.query(),
      limit=util.param('limit', int),
      cursor=util.param('cursor'),
      order=util.param('order') or '-created',
      name=util.param('name'),
      admin=util.param('admin', bool),
    )

  if flask.request.path.startswith('/_s/'):
    return util.jsonify_model_dbs(user_dbs, more_cursor)

  return flask.render_template(
      'user_list.html',
      html_class='user',
      title='User List',
      user_dbs=user_dbs,
      more_url=util.generate_more_url(more_cursor),
    )


################################################################################
# Error Handling
################################################################################
@app.errorhandler(400)
@app.errorhandler(401)
@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(410)
@app.errorhandler(418)
@app.errorhandler(500)
def error_handler(e):
  try:
    e.code
  except:
    class e(object):
      code = 500
      name = 'Internal Server Error'

  if flask.request.path.startswith('/_s/'):
    return flask.jsonify({
        'status': 'error',
        'error_code': e.code,
        'error_name': e.name.lower().replace(' ', '_'),
        'error_message': e.name,
      }), e.code

  return flask.render_template(
      'error.html',
      title='Error %d (%s)!!1' % (e.code, e.name),
      html_class='error-page',
      error=e,
    ), e.code
