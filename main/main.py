import sys
if not ('lib.zip' in sys.path):
  sys.path.insert(0, 'lib.zip')

import flask
from flaskext import wtf
import config

app = flask.Flask(__name__)
app.config.from_object(config)

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
      channel_name='welcome',
    )


################################################################################
# Profile stuff
################################################################################
class ProfileUpdateForm(wtf.Form):
  name = wtf.TextField('Name', [wtf.validators.required()])
  email = wtf.TextField('Email', [
      wtf.validators.optional(),
      wtf.validators.email("That doesn't look like an email"),
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
  feedback = wtf.TextAreaField('Feedback', [wtf.validators.required()])
  email = wtf.TextField('Email (optional)', [
      wtf.validators.optional(),
      wtf.validators.email("That doesn't look like an email"),
    ])


@app.route('/feedback/', methods=['GET', 'POST'])
def feedback():
  form = FeedbackForm()
  if form.validate_on_submit():
    mail.send_mail(
        sender=model.Config.get_master_db().feedback_email,
        to=model.Config.get_master_db().feedback_email,
        subject='[%s] %s' % (
            model.Config.get_master_db().brand_name,
            form.subject.data,
          ),
        reply_to=form.email.data or model.Config.get_master_db().feedback_email,
        body=form.feedback.data,
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
def user_list():
  user_dbs, more_cursor = util.retrieve_dbs(
      model.User,
      model.User.query(),
      limit=util.param('limit', int),
      cursor=util.param('cursor'),
      order=util.param('order'),
      name=util.param('name'),
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
# Extras
################################################################################
@app.route('/_s/extras/', endpoint='extras_service')
@app.route('/extras/', endpoint='extras')
def extras():
  country = None
  region = None
  city = None
  city_lat_long = None
  if 'X-AppEngine-Country' in flask.request.headers:
    country = flask.request.headers['X-AppEngine-Country']
  if 'X-AppEngine-Region' in flask.request.headers:
    region = flask.request.headers['X-AppEngine-Region']
  if 'X-AppEngine-City' in flask.request.headers:
    city = flask.request.headers['X-AppEngine-City']
  if 'X-AppEngine-CityLatLong' in flask.request.headers:
    city_lat_long = flask.request.headers['X-AppEngine-CityLatLong']

  extra_info = {
    'country': country,
    'region': region,
    'city': city,
    'city_lat_long': city_lat_long,
    'user_agent': flask.request.headers['User-Agent'],
  }

  if flask.request.path.startswith('/_s/'):
    return flask.jsonify(extra_info)

  return flask.render_template(
      'extras.html',
      html_class='extras',
      title='Extras',
      extra_info=extra_info,
    )


@app.route('/chat/')
def chat():
  return flask.render_template(
      'chat.html',
      title='Chat',
      html_class='chat',
      channel_name='chat',
    )

