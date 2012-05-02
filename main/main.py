import sys
if not ('lib' in sys.path):
  sys.path.insert(0, 'lib')

import flask
from flaskext import wtf
import config

app = flask.Flask(__name__)
app.config.from_object(config)

import auth
import util
import model


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
      'user.html',
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
