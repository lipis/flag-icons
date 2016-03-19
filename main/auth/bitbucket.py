# coding: utf-8

import flask

import auth
import config
import model
import util

from main import app

bitbucket_config = dict(
  access_token_method='POST',
  access_token_url='https://bitbucket.org/site/oauth2/access_token',
  authorize_url='https://bitbucket.org/site/oauth2/authorize',
  base_url='https://api.bitbucket.org/2.0/',
  consumer_key=config.CONFIG_DB.bitbucket_key,
  consumer_secret=config.CONFIG_DB.bitbucket_secret,
)

bitbucket = auth.create_oauth_app(bitbucket_config, 'bitbucket')


@app.route('/api/auth/callback/bitbucket/')
def bitbucket_authorized():
  response = bitbucket.authorized_response()
  if response is None:
    flask.flash('You denied the request to sign in.')
    return flask.redirect(util.get_next_url())

  flask.session['oauth_token'] = (response['access_token'], '')
  me = bitbucket.get('user')
  user_db = retrieve_user_from_bitbucket(me.data)
  return auth.signin_user_db(user_db)


@bitbucket.tokengetter
def get_bitbucket_oauth_token():
  return flask.session.get('oauth_token')


@app.route('/signin/bitbucket/')
def signin_bitbucket():
  return auth.signin_oauth(bitbucket)


def retrieve_user_from_bitbucket(response):
  auth_id = 'bitbucket_%s' % response['username']
  user_db = model.User.get_by('auth_ids', auth_id)
  if user_db:
    return user_db
  emails = bitbucket.get('user/emails').data['values']
  email = ''.join([e['email'] for e in emails if e['is_primary']][0:1])
  return auth.create_user_db(
    auth_id=auth_id,
    name=response['display_name'],
    username=response['username'],
    email=email,
    verified=bool(email),
  )
