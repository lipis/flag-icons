from google.appengine.ext import ndb
from google.appengine.api import users

import functools

import flask
import flaskext.login
import flaskext.oauth

import util
import model
import config

from main import app


################################################################################
# Flaskext Login
################################################################################
login_manager = flaskext.login.LoginManager()


class AnonymousUser(flaskext.login.AnonymousUser):
  id = 0
  admin = False
  name = 'Anonymous'

  def key(self):
    return None

login_manager.anonymous_user = AnonymousUser


class FlaskUser(AnonymousUser):
  def __init__(self, user_db):
    self.user_db = user_db
    self.id = user_db.key.id()
    self.name = user_db.name
    self.admin = user_db.admin

  def key(self):
    return self.user_db.key.urlsafe()

  def get_id(self):
    return self.user_db.key.urlsafe()

  def is_authenticated(self):
    return True

  def is_active(self):
    return self.user_db.active

  def is_anonymous(self):
    return False


@login_manager.user_loader
def load_user(key):
  user_db = ndb.Key(urlsafe=key).get()
  if user_db:
    return FlaskUser(user_db)
  return None


login_manager.setup_app(app)


def current_user_id():
  return flaskext.login.current_user.id


def current_user_key():
  return flaskext.login.current_user.user_db.key


def current_user_db():
  return current_user_key().get()


def is_logged_in():
  return current_user_id() != 0


def login_required(f):
  @functools.wraps(f)
  def decorated_function(*args, **kws):
    if is_logged_in():
      return f(*args, **kws)
    if flask.request.path.startswith('/_s/'):
      return flask.abort(401)
    return flask.redirect(flask.url_for('signin', next=flask.request.url))
  return decorated_function


def admin_required(f):
  @functools.wraps(f)
  def decorated_function(*args, **kws):
    if is_logged_in() and current_user_db().admin:
      return f(*args, **kws)
    if not is_logged_in() and flask.request.path.startswith('/_s/'):
      return flask.abort(401)
    if not is_logged_in():
      return flask.redirect(flask.url_for('signin', next=flask.request.url))
    return flask.abort(403)
  return decorated_function


################################################################################
# Sign in stuff
################################################################################
@app.route('/login/')
@app.route('/signin/')
def signin():
  next_url = util.get_next_url()
  if flask.url_for('signin') in next_url:
    next_url = flask.url_for('welcome')

  google_signin_url = flask.url_for('signin_google', next=next_url)
  twitter_signin_url = flask.url_for('signin_twitter', next=next_url)
  facebook_signin_url = flask.url_for('signin_facebook', next=next_url)

  return flask.render_template(
      'signin.html',
      title='Please sign in',
      html_class='signin',
      google_signin_url=google_signin_url,
      twitter_signin_url=twitter_signin_url,
      facebook_signin_url=facebook_signin_url,
      next_url=next_url,
    )


@app.route('/signout/')
def signout():
  flaskext.login.logout_user()
  flask.flash(u'You have been signed out.')
  return flask.redirect(flask.url_for('welcome'))


################################################################################
# Google
################################################################################
@app.route('/signin/google/')
def signin_google():
  google_url = users.create_login_url(
      flask.url_for('google_authorized', next=util.get_next_url())
    )
  return flask.redirect(google_url)


@app.route('/_s/callback/google/authorized/')
def google_authorized():
  google_user = users.get_current_user()
  if google_user is None:
    flask.flash(u'You denied the request to sign in.')
    return flask.redirect(util.get_next_url())

  user_db = retrieve_user_from_google(google_user)
  return signin_user_db(user_db)


def retrieve_user_from_google(google_user):
  user_db = model.User.retrieve_one_by('federated_id', google_user.user_id())
  if user_db:
    if not user_db.admin and users.is_current_user_admin():
      user_db.admin = True
      user_db.put()
    return user_db
  user_db = model.User(
      federated_id=google_user.user_id(),
      name=strip_username_from_email(google_user.nickname()),
      username=generate_unique_username(google_user.nickname()),
      email=google_user.email().lower(),
      admin=users.is_current_user_admin(),
    )
  user_db.put()
  return user_db


################################################################################
# Twitter
################################################################################
twitter_oauth = flaskext.oauth.OAuth()


twitter = twitter_oauth.remote_app(
    'twitter',
    base_url='http://api.twitter.com/1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
    consumer_key=config.CONFIG_DB.twitter_consumer_key,
    consumer_secret=config.CONFIG_DB.twitter_consumer_secret,
  )


@app.route('/_s/callback/twitter/oauth-authorized/')
@twitter.authorized_handler
def twitter_oauth_authorized(resp):
  if resp is None:
    flask.flash(u'You denied the request to sign in.')
    return flask.redirect(util.get_next_url())

  flask.session['oauth_token'] = (
    resp['oauth_token'],
    resp['oauth_token_secret']
  )
  user_db = retrieve_user_from_twitter(resp)
  return signin_user_db(user_db)


@twitter.tokengetter
def get_twitter_token():
  return flask.session.get('oauth_token')


@app.route('/signin/twitter/')
def signin_twitter():
  flask.session.pop('oauth_token', None)
  try:
    return twitter.authorize(
        callback=flask.url_for('twitter_oauth_authorized',
        next=util.get_next_url()),
      )
  except:
    flask.flash(
        'Something went terribly wrong with Twitter sign in. Please try again.',
        category='danger',
      )
    return flask.redirect(flask.url_for('signin', next=util.get_next_url()))


def retrieve_user_from_twitter(response):
  user_db = model.User.retrieve_one_by('twitter_id', response['user_id'])
  if user_db:
    return user_db
  user_db = model.User(
      twitter_id=response['user_id'],
      name=response['screen_name'],
      username=generate_unique_username(response['screen_name']),
    )
  user_db.put()
  return user_db


################################################################################
# Facebook
################################################################################
facebook_oauth = flaskext.oauth.OAuth()

facebook = facebook_oauth.remote_app(
    'facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=config.CONFIG_DB.facebook_app_id,
    consumer_secret=config.CONFIG_DB.facebook_app_secret,
    request_token_params={'scope': 'email'},
  )


@app.route('/_s/callback/facebook/oauth-authorized/')
@facebook.authorized_handler
def facebook_authorized(resp):
  if resp is None:
    return 'Access denied: reason=%s error=%s' % (
      flask.request.args['error_reason'],
      flask.request.args['error_description']
    )
  flask.session['oauth_token'] = (resp['access_token'], '')
  me = facebook.get('/me')
  user_db = retrieve_user_from_facebook(me.data)
  return signin_user_db(user_db)


@facebook.tokengetter
def get_facebook_oauth_token():
  return flask.session.get('oauth_token')


@app.route('/signin/facebook/')
def signin_facebook():
  return facebook.authorize(callback=flask.url_for('facebook_authorized',
      next=util.get_next_url(),
      _external=True),
    )


def retrieve_user_from_facebook(response):
  user_db = model.User.retrieve_one_by('facebook_id', response['id'])
  if user_db:
    return user_db

  if 'username' in response:
    username = response['username']
  else:
    username = response['id']

  user_db = model.User(
      facebook_id=response['id'],
      name=response['name'],
      email=response['email'].lower(),
      username=generate_unique_username(username),
    )
  user_db.put()
  return user_db


################################################################################
# Helpers
################################################################################
def signin_user_db(user_db):
  if not user_db:
    return flask.redirect(flask.url_for('signin'))

  flask_user_db = FlaskUser(user_db)
  if flaskext.login.login_user(flask_user_db):
    flask.flash('Hello %s, welcome to %s!!!' % (
        user_db.name, config.CONFIG_DB.brand_name,
      ), category='success')
    return flask.redirect(util.get_next_url())
  else:
    flask.flash('Sorry, but you could not sign in.', category='danger')
    return flask.redirect(flask.url_for('signin'))


def strip_username_from_email(email):
  #TODO: use re
  if email.find('@') > 0:
    email = email[0:email.find('@')]
  return email.lower()


def generate_unique_username(username):
  username = strip_username_from_email(username)

  new_username = username
  n = 1
  while model.User.retrieve_one_by('username', new_username) is not None:
    new_username = '%s%d' % (username, n)
    n += 1
  return new_username
