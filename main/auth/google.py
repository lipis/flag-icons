# coding: utf-8

import flask

import auth
import config
import model
import util

from main import app

google_config = dict(
  access_token_method='POST',
  access_token_url='https://accounts.google.com/o/oauth2/token',
  authorize_url='https://accounts.google.com/o/oauth2/auth',
  base_url='https://www.googleapis.com/plus/v1/people/',
  consumer_key=config.CONFIG_DB.google_client_id,
  consumer_secret=config.CONFIG_DB.google_client_secret,
  request_token_params={'scope': 'email profile'},
)

google = auth.create_oauth_app(google_config, 'google')


@app.route('/api/auth/callback/google/')
def google_authorized():
  response = google.authorized_response()
  if response is None:
    flask.flash('You denied the request to sign in.')
    return flask.redirect(util.get_next_url())

  flask.session['oauth_token'] = (response['access_token'], '')
  me = google.get('me', data={'access_token': response['access_token']})
  user_db = retrieve_user_from_google(me.data)
  return auth.signin_user_db(user_db)


@google.tokengetter
def get_google_oauth_token():
  return flask.session.get('oauth_token')


@app.route('/signin/google/')
def signin_google():
  return auth.signin_oauth(google)


def retrieve_user_from_google(response):
  auth_id = 'google_%s' % response['id']
  user_db = model.User.get_by('auth_ids', auth_id)
  if user_db:
    return user_db

  if 'email' in response:
    email = response['email']
  elif 'emails' in response:
    email = response['emails'][0]['value']
  else:
    email = ''

  if 'displayName' in response:
    name = response['displayName']
  elif 'name' in response:
    names = response['name']
    given_name = names.get('givenName', '')
    family_name = names.get('familyName', '')
    name = ' '.join([given_name, family_name]).strip()
  else:
    name = 'google_user_%s' % id

  return auth.create_user_db(
    auth_id=auth_id,
    name=name,
    username=email or name,
    email=email,
    verified=bool(email),
  )
