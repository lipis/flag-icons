# coding: utf-8

import functools
import re

from flask.ext import login
from flask.ext import wtf
from flask.ext.oauthlib import client as oauth
from google.appengine.api import users
from google.appengine.ext import ndb
import flask
import unidecode
import wtforms


import cache
import config
import model
import task
import util

from main import app

_signals = flask.signals.Namespace()

###############################################################################
# Flask Login
###############################################################################
login_manager = login.LoginManager()


class AnonymousUser(login.AnonymousUserMixin):
  id = 0
  admin = False
  name = 'Anonymous'
  user_db = None

  def key(self):
    return None

  def has_permission(self, permission):
    return False

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

  def has_permission(self, permission):
    return self.user_db.has_permission(permission)


@login_manager.user_loader
def load_user(key):
  user_db = ndb.Key(urlsafe=key).get()
  if user_db:
    return FlaskUser(user_db)
  return None


login_manager.init_app(app)


def current_user_id():
  return login.current_user.id


def current_user_key():
  return login.current_user.user_db.key if login.current_user.user_db else None


def current_user_db():
  return login.current_user.user_db


def is_logged_in():
  return login.current_user.id != 0


###############################################################################
# Decorators
###############################################################################
def login_required(f):
  decorator_order_guard(f, 'auth.login_required')

  @functools.wraps(f)
  def decorated_function(*args, **kws):
    if is_logged_in():
      return f(*args, **kws)
    if flask.request.path.startswith('/_s/'):
      return flask.abort(401)
    return flask.redirect(flask.url_for('signin', next=flask.request.url))
  return decorated_function


def admin_required(f):
  decorator_order_guard(f, 'auth.admin_required')

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


permission_registered = _signals.signal('permission-registered')


def permission_required(permission=None, methods=None):
  def permission_decorator(f):
    decorator_order_guard(f, 'auth.permission_required')

    # default to decorated function name as permission
    perm = permission or f.func_name
    meths = [m.upper() for m in methods] if methods else None

    permission_registered.send(f, permission=perm)

    @functools.wraps(f)
    def decorated_function(*args, **kws):
      if meths and flask.request.method.upper() not in meths:
        return f(*args, **kws)
      if is_logged_in() and current_user_db().has_permission(perm):
        return f(*args, **kws)
      if not is_logged_in():
        if flask.request.path.startswith('/_s/'):
          return flask.abort(401)
        return flask.redirect(flask.url_for('signin', next=flask.request.url))
      return flask.abort(403)
    return decorated_function
  return permission_decorator


###############################################################################
# Sign in/up stuff
###############################################################################
class SignInForm(wtf.Form):
  email = wtforms.StringField(
      'Email',
      [wtforms.validators.required()],
      filters=[util.email_filter],
    )
  password = wtforms.StringField(
      'Password',
      [wtforms.validators.required()],
    )
  remember = wtforms.BooleanField(
      'Keep me signed in',
      [wtforms.validators.optional()],
    )
  recaptcha = wtf.RecaptchaField('Are you human?')
  next_url = wtforms.HiddenField()


class SignUpForm(wtf.Form):
  email = wtforms.StringField(
      'Email',
      [wtforms.validators.required(), wtforms.validators.email()],
      filters=[util.email_filter],
    )
  recaptcha = wtf.RecaptchaField('Are you human?')


@app.route('/signup/', methods=['GET', 'POST'], endpoint='signup')
@app.route('/signin/', methods=['GET', 'POST'], endpoint='signin')
def auth():
  auth_type = 'open'
  if config.CONFIG_DB.has_email_authentication:
    auth_type = 'signin'
    if flask.url_for('signup') in flask.request.path:
      auth_type = 'signup'

  next_url = util.get_next_url()
  google_signin_url = url_for_signin('google', next_url)
  twitter_signin_url = url_for_signin('twitter', next_url)
  facebook_signin_url = url_for_signin('facebook', next_url)
  form = None
  hide_recaptcha = cache.get_auth_attempt() < config.RECAPTCHA_LIMIT

  # --------------
  # Sign in stuff
  # --------------
  if auth_type == 'signin':
    form = SignInForm()
    if hide_recaptcha or not config.CONFIG_DB.has_recaptcha:
      del form.recaptcha
    save_request_params()
    if form.validate_on_submit():
      result = retrieve_user_from_email(form.email.data, form.password.data)
      if result:
        cache.reset_auth_attempt()
        return signin_user_db(result)
      if result is None:
        form.email.errors.append('Email or Password do not match')
      if result is False:
        return flask.redirect(flask.url_for('welcome'))
    if not form.errors:
      form.next_url.data = next_url

  # --------------
  # Sign up stuff
  # --------------
  if auth_type == 'signup':
    form = SignUpForm()
    if hide_recaptcha or not config.CONFIG_DB.has_recaptcha:
      del form.recaptcha
    save_request_params()
    if form.validate_on_submit():
      user_db = model.User.get_by('email', form.email.data)
      if user_db:
        form.email.errors.append('This email is already taken.')

      if not form.errors:
        user_db = create_user_db(
            None,
            util.create_name_from_email(form.email.data),
            form.email.data,
            form.email.data,
          )
        user_db.put()
        task.activate_user_notification(user_db)
        cache.bump_auth_attempt()
        return flask.redirect(flask.url_for('welcome'))

  if form and form.errors:
    cache.bump_auth_attempt()

  return flask.render_template(
      'auth/auth.html',
      title='Sign up' if auth_type == 'signup' else 'Sign in',
      html_class='auth %s' % auth_type,
      google_signin_url=google_signin_url,
      twitter_signin_url=twitter_signin_url,
      facebook_signin_url=facebook_signin_url,
      next_url=next_url,
      form=form,
      auth_type=auth_type,
    )


@app.route('/signout/')
def signout():
  login.logout_user()
  flask.flash(u'You have been signed out.', category='success')
  return flask.redirect(util.param('next') or flask.url_for('signin'))


###############################################################################
# Google
###############################################################################
@app.route('/signin/google/')
def signin_google():
  save_request_params()
  google_url = users.create_login_url(flask.url_for('google_authorized'))
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
  auth_id = 'federated_%s' % google_user.user_id()
  user_db = model.User.get_by('auth_ids', auth_id)
  if user_db:
    if not user_db.admin and users.is_current_user_admin():
      user_db.admin = True
      user_db.put()
    return user_db

  return create_user_db(
      auth_id,
      util.create_name_from_email(google_user.email()),
      google_user.email(),
      google_user.email(),
      verified=True,
      admin=users.is_current_user_admin(),
    )


###############################################################################
# Twitter
###############################################################################
twitter_oauth = oauth.OAuth()

app.config['TWITTER'] = dict(
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authorize',
    consumer_key=config.CONFIG_DB.twitter_consumer_key,
    consumer_secret=config.CONFIG_DB.twitter_consumer_secret,
  )

twitter = twitter_oauth.remote_app('twitter', app_key='TWITTER')
twitter_oauth.init_app(app)


@app.route('/_s/callback/twitter/oauth-authorized/')
def twitter_authorized():
  resp = twitter.authorized_response()
  if resp is None:
    flask.flash(u'You denied the request to sign in.')
    return flask.redirect(util.get_next_url())

  flask.session['oauth_token'] = (
      resp['oauth_token'],
      resp['oauth_token_secret'],
    )
  user_db = retrieve_user_from_twitter(resp)
  return signin_user_db(user_db)


@twitter.tokengetter
def get_twitter_token():
  return flask.session.get('oauth_token')


@app.route('/signin/twitter/')
def signin_twitter():
  try:
    return signin_oauth(twitter)
  except:
    flask.flash(
        'Something went wrong with Twitter sign in. Please try again.',
        category='danger',
      )
    return flask.redirect(flask.url_for('signin', next=util.get_next_url()))


def retrieve_user_from_twitter(response):
  auth_id = 'twitter_%s' % response['user_id']
  user_db = model.User.get_by('auth_ids', auth_id)
  if user_db:
    return user_db

  return create_user_db(
      auth_id,
      response['screen_name'],
      response['screen_name'],
    )


###############################################################################
# Facebook
###############################################################################
facebook_oauth = oauth.OAuth()

app.config['FACEBOOK'] = dict(
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=config.CONFIG_DB.facebook_app_id,
    consumer_secret=config.CONFIG_DB.facebook_app_secret,
    request_token_params={'scope': 'email'},
  )

facebook = facebook_oauth.remote_app('facebook', app_key='FACEBOOK')
facebook_oauth.init_app(app)


@app.route('/_s/callback/facebook/oauth-authorized/')
def facebook_authorized():
  resp = facebook.authorized_response()
  if resp is None:
    flask.flash(u'You denied the request to sign in.')
    return flask.redirect(util.get_next_url())

  flask.session['oauth_token'] = (resp['access_token'], '')
  me = facebook.get('/me')
  user_db = retrieve_user_from_facebook(me.data)
  return signin_user_db(user_db)


@facebook.tokengetter
def get_facebook_oauth_token():
  return flask.session.get('oauth_token')


@app.route('/signin/facebook/')
def signin_facebook():
  return signin_oauth(facebook)


def retrieve_user_from_facebook(response):
  auth_id = 'facebook_%s' % response['id']
  user_db = model.User.get_by('auth_ids', auth_id)
  if user_db:
    return user_db
  return create_user_db(
      auth_id,
      response['name'],
      response.get('username', response['name']),
      response.get('email', ''),
      verified=bool(response.get('email', '')),
    )


###############################################################################
# Helpers
###############################################################################
def decorator_order_guard(f, decorator_name):
  if f in app.view_functions.values():
    raise SyntaxError(
        'Do not use %s above app.route decorators as it would not be checked. '
        'Instead move the line below the app.route lines.' % decorator_name
      )


def create_user_db(auth_id, name, username, email='', verified=False, **props):
  email = email.lower() if email else ''
  if verified and email:
    user_dbs, user_cr = model.User.get_dbs(email=email, verified=True, limit=2)
    if len(user_dbs) == 1:
      user_db = user_dbs[0]
      user_db.auth_ids.append(auth_id)
      user_db.put()
      task.new_user_notification(user_db)
      return user_db

  if isinstance(username, str):
    username = username.decode('utf-8')
  username = unidecode.unidecode(username.split('@')[0].lower()).strip()
  username = re.sub(r'[\W_]+', '.', username)
  new_username = username
  n = 1
  while not model.User.is_username_available(new_username):
    new_username = '%s%d' % (username, n)
    n += 1

  user_db = model.User(
      name=name,
      email=email,
      username=new_username,
      auth_ids=[auth_id] if auth_id else [],
      verified=verified,
      token=util.uuid(),
      **props
    )
  user_db.put()
  task.new_user_notification(user_db)
  return user_db


def save_request_params():
  flask.session['auth-params'] = {
      'next': util.get_next_url(),
      'remember': util.param('remember', bool),
    }


def signin_oauth(oauth_app, scheme='http'):
  flask.session.pop('oauth_token', None)
  save_request_params()
  return oauth_app.authorize(callback=flask.url_for(
    '%s_authorized' % oauth_app.name, _external=True, _scheme=scheme
  ))


def url_for_signin(service_name, next_url):
  return flask.url_for('signin_%s' % service_name, next=next_url)


@ndb.toplevel
def signin_user_db(user_db):
  if not user_db:
    return flask.redirect(flask.url_for('signin'))
  flask_user_db = FlaskUser(user_db)
  auth_params = flask.session.get('auth-params', {
      'next': flask.url_for('welcome'),
      'remember': False,
    })
  flask.session.pop('auth-params', None)
  if login.login_user(flask_user_db, remember=auth_params['remember']):
    user_db.put_async()
    flask.flash('Hello %s, welcome to %s.' % (
        user_db.name, config.CONFIG_DB.brand_name,
      ), category='success')
    return flask.redirect(util.get_next_url(auth_params['next']))
  flask.flash('Sorry, but you could not sign in.', category='danger')
  return flask.redirect(flask.url_for('signin'))


def retrieve_user_from_email(email, password):
  user_dbs, user_cursor = model.User.get_dbs(email=email, active=True, limit=2)
  if not user_dbs:
    return None
  if len(user_dbs) > 1:
    flask.flash('''We are sorry but it looks like there is a conflict with your
        account. Our support team is already informed and we will get back to
        you as soon as possible.''', category='danger')
    task.email_conflict_notification(email)
    return False

  user_db = user_dbs[0]
  if user_db.password_hash == util.password_hash(user_db, password):
    return user_db
  return None
