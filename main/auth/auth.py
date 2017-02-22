# coding: utf-8

from __future__ import absolute_import

import functools
import re

from flask_oauthlib import client as oauth
from google.appengine.ext import ndb
import flask
import flask_login
import flask_wtf
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
login_manager = flask_login.LoginManager()


class AnonymousUser(flask_login.AnonymousUserMixin):
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
  return flask_login.current_user.id


def current_user_key():
  return flask_login.current_user.user_db.key if flask_login.current_user.user_db else None


def current_user_db():
  return flask_login.current_user.user_db


def is_logged_in():
  return flask_login.current_user.id != 0


###############################################################################
# Decorators
###############################################################################
def login_required(f):
  decorator_order_guard(f, 'auth.login_required')

  @functools.wraps(f)
  def decorated_function(*args, **kwargs):
    if is_logged_in():
      return f(*args, **kwargs)
    if flask.request.path.startswith('/api/'):
      return flask.abort(401)
    return flask.redirect(flask.url_for('signin', next=flask.request.url))

  return decorated_function


def admin_required(f):
  decorator_order_guard(f, 'auth.admin_required')

  @functools.wraps(f)
  def decorated_function(*args, **kwargs):
    if is_logged_in() and current_user_db().admin:
      return f(*args, **kwargs)
    if not is_logged_in() and flask.request.path.startswith('/api/'):
      return flask.abort(401)
    if not is_logged_in():
      return flask.redirect(flask.url_for('signin', next=flask.request.url))
    return flask.abort(403)

  return decorated_function


def cron_required(f):
  decorator_order_guard(f, 'auth.cron_required')

  @functools.wraps(f)
  def decorated_function(*args, **kwargs):
    if 'X-Appengine-Cron' in flask.request.headers:
      return f(*args, **kwargs)
    if is_logged_in() and current_user_db().admin:
      return f(*args, **kwargs)
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
    def decorated_function(*args, **kwargs):
      if meths and flask.request.method.upper() not in meths:
        return f(*args, **kwargs)
      if is_logged_in() and current_user_db().has_permission(perm):
        return f(*args, **kwargs)
      if not is_logged_in():
        if flask.request.path.startswith('/api/'):
          return flask.abort(401)
        return flask.redirect(flask.url_for('signin', next=flask.request.url))
      return flask.abort(403)

    return decorated_function

  return permission_decorator


###############################################################################
# Sign in stuff
###############################################################################
class SignInForm(flask_wtf.FlaskForm):
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
  recaptcha = flask_wtf.RecaptchaField()
  next_url = wtforms.HiddenField()


@app.route('/signin/', methods=['GET', 'POST'])
def signin():
  next_url = util.get_next_url()
  form = None
  if config.CONFIG_DB.has_email_authentication:
    form = form_with_recaptcha(SignInForm())
    save_request_params()
    if form.validate_on_submit():
      result = get_user_db_from_email(form.email.data, form.password.data)
      if result:
        cache.reset_auth_attempt()
        return signin_user_db(result)
      if result is None:
        form.email.errors.append('Email or Password do not match')
      if result is False:
        return flask.redirect(flask.url_for('welcome'))
    if not form.errors:
      form.next_url.data = next_url

  if form and form.errors:
    cache.bump_auth_attempt()

  return flask.render_template(
    'auth/auth.html',
    title='Sign in',
    html_class='auth',
    next_url=next_url,
    form=form,
    form_type='signin' if config.CONFIG_DB.has_email_authentication else '',
    **urls_for_oauth(next_url)
  )


###############################################################################
# Sign up stuff
###############################################################################
class SignUpForm(flask_wtf.FlaskForm):
  email = wtforms.StringField(
    'Email',
    [wtforms.validators.required(), wtforms.validators.email()],
    filters=[util.email_filter],
  )
  recaptcha = flask_wtf.RecaptchaField()


@app.route('/signup/', methods=['GET', 'POST'])
def signup():
  next_url = util.get_next_url()
  form = None
  if config.CONFIG_DB.has_email_authentication:
    form = form_with_recaptcha(SignUpForm())
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

  title = 'Sign up' if config.CONFIG_DB.has_email_authentication else 'Sign in'
  return flask.render_template(
    'auth/auth.html',
    title=title,
    html_class='auth',
    next_url=next_url,
    form=form,
    **urls_for_oauth(next_url)
  )


###############################################################################
# Sign out stuff
###############################################################################
@app.route('/signout/')
def signout():
  flask_login.logout_user()
  return flask.redirect(util.param('next') or flask.url_for('signin'))


###############################################################################
# Helpers
###############################################################################
def url_for_signin(service_name, next_url):
  return flask.url_for('signin_%s' % service_name, next=next_url)


def urls_for_oauth(next_url):
  return {
    'azure_ad_signin_url': url_for_signin('azure_ad', next_url),
    'bitbucket_signin_url': url_for_signin('bitbucket', next_url),
    'dropbox_signin_url': url_for_signin('dropbox', next_url),
    'facebook_signin_url': url_for_signin('facebook', next_url),
    'github_signin_url': url_for_signin('github', next_url),
    'google_signin_url': url_for_signin('google', next_url),
    'gae_signin_url': url_for_signin('gae', next_url),
    'instagram_signin_url': url_for_signin('instagram', next_url),
    'linkedin_signin_url': url_for_signin('linkedin', next_url),
    'mailru_signin_url': url_for_signin('mailru', next_url),
    'microsoft_signin_url': url_for_signin('microsoft', next_url),
    'reddit_signin_url': url_for_signin('reddit', next_url),
    'twitter_signin_url': url_for_signin('twitter', next_url),
    'vk_signin_url': url_for_signin('vk', next_url),
    'yahoo_signin_url': url_for_signin('yahoo', next_url),
  }


def create_oauth_app(service_config, name):
  upper_name = name.upper()
  app.config[upper_name] = service_config
  service_oauth = oauth.OAuth()
  service_app = service_oauth.remote_app(name, app_key=upper_name)
  service_oauth.init_app(app)
  return service_app


def decorator_order_guard(f, decorator_name):
  if f in app.view_functions.values():
    raise SyntaxError(
      'Do not use %s above app.route decorators as it would not be checked. '
      'Instead move the line below the app.route lines.' % decorator_name
    )


def save_request_params():
  flask.session['auth-params'] = {
    'next': util.get_next_url(),
    'remember': util.param('remember'),
  }


def signin_oauth(oauth_app, scheme=None):
  try:
    flask.session.pop('oauth_token', None)
    save_request_params()
    return oauth_app.authorize(callback=flask.url_for(
      '%s_authorized' % oauth_app.name, _external=True, _scheme=scheme
    ))
  except oauth.OAuthException:
    flask.flash(
      'Something went wrong with sign in. Please try again.',
      category='danger',
    )
    return flask.redirect(flask.url_for('signin', next=util.get_next_url()))


def form_with_recaptcha(form):
  should_have_recaptcha = cache.get_auth_attempt() >= config.RECAPTCHA_LIMIT
  if not (should_have_recaptcha and config.CONFIG_DB.has_recaptcha):
    del form.recaptcha
  return form


###############################################################################
# User related stuff
###############################################################################
def create_user_db(auth_id, name, username, email='', verified=False, **props):
  email = email.lower() if email else ''
  if verified and email:
    user_dbs, cursors = model.User.get_dbs(email=email, verified=True, limit=2)
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
  if flask_login.login_user(flask_user_db, remember=auth_params['remember']):
    user_db.put_async()
    return flask.redirect(util.get_next_url(auth_params['next']))
  flask.flash('Sorry, but you could not sign in.', category='danger')
  return flask.redirect(flask.url_for('signin'))


def get_user_db_from_email(email, password):
  user_dbs, cursors = model.User.get_dbs(email=email, active=True, limit=2)
  if not user_dbs:
    return None
  if len(user_dbs) > 1:
    flask.flash('''We are sorry but it looks like there is a conflict with
        your account. Our support team has been informed and we will get
        back to you as soon as possible.''', category='danger')
    task.email_conflict_notification(email)
    return False

  user_db = user_dbs[0]
  if user_db.password_hash == util.password_hash(user_db, password):
    return user_db
  return None
