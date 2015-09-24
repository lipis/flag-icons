# coding: utf-8

import flask

import auth
import config
import model
import util

from main import app


facebook_config = dict(
    access_token_url='/oauth/access_token',
    authorize_url='/oauth/authorize',
    base_url='https://graph.facebook.com/',
    consumer_key=config.CONFIG_DB.facebook_app_id,
    consumer_secret=config.CONFIG_DB.facebook_app_secret,
    request_token_params={'scope': 'email'},
  )

facebook = auth.create_oauth_app(facebook_config, 'facebook')


@app.route('/api/auth/callback/facebook/')
def facebook_authorized():
  response = facebook.authorized_response()
  if response is None:
    flask.flash('You denied the request to sign in.')
    return flask.redirect(util.get_next_url())

  flask.session['oauth_token'] = (response['access_token'], '')
  me = facebook.get('/me?fields=name,email')
  user_db = retrieve_user_from_facebook(me.data)
  return auth.signin_user_db(user_db)


@facebook.tokengetter
def get_facebook_oauth_token():
  return flask.session.get('oauth_token')


@app.route('/signin/facebook/')
def signin_facebook():
  return auth.signin_oauth(facebook)


def retrieve_user_from_facebook(response):
  auth_id = 'facebook_%s' % response['id']
  user_db = model.User.get_by('auth_ids', auth_id)
  return user_db or auth.create_user_db(
      auth_id=auth_id,
      name=response['name'],
      username=response.get('username', response['name']),
      email=response.get('email', ''),
      verified=bool(response.get('email', '')),
    )
