# coding: utf-8

import flask

import auth
import model
import util

from main import app

instagram_config = dict(
  access_token_method='POST',
  access_token_url='https://api.instagram.com/oauth/access_token',
  authorize_url='https://instagram.com/oauth/authorize/',
  base_url='https://api.instagram.com/v1',
  consumer_key=model.Config.get_master_db().instagram_client_id,
  consumer_secret=model.Config.get_master_db().instagram_client_secret,
)

instagram = auth.create_oauth_app(instagram_config, 'instagram')


@app.route('/api/auth/callback/instagram/')
def instagram_authorized():
  response = instagram.authorized_response()
  if response is None:
    flask.flash('You denied the request to sign in.')
    return flask.redirect(util.get_next_url())

  flask.session['oauth_token'] = (response['access_token'], '')
  user_db = retrieve_user_from_instagram(response['user'])
  return auth.signin_user_db(user_db)


@instagram.tokengetter
def get_instagram_oauth_token():
  return flask.session.get('oauth_token')


@app.route('/signin/instagram/')
def signin_instagram():
  return auth.signin_oauth(instagram)


def retrieve_user_from_instagram(response):
  auth_id = 'instagram_%s' % response['id']
  user_db = model.User.get_by('auth_ids', auth_id)
  if user_db:
    return user_db

  return auth.create_user_db(
    auth_id=auth_id,
    name=response.get('full_name', '').strip() or response.get('username'),
    username=response.get('username'),
  )
