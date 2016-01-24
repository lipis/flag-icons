# coding: utf-8

import flask

import auth
import config
import model
import util

from main import app

dropbox_config = dict(
  access_token_method='POST',
  access_token_url='https://api.dropbox.com/1/oauth2/token',
  authorize_url='https://www.dropbox.com/1/oauth2/authorize',
  base_url='https://www.dropbox.com/1/',
  consumer_key=config.CONFIG_DB.dropbox_app_key,
  consumer_secret=config.CONFIG_DB.dropbox_app_secret,
)

dropbox = auth.create_oauth_app(dropbox_config, 'dropbox')


@app.route('/api/auth/callback/dropbox/')
def dropbox_authorized():
  response = dropbox.authorized_response()
  if response is None:
    flask.flash('You denied the request to sign in.')
    return flask.redirect(util.get_next_url())
  flask.session['oauth_token'] = (response['access_token'], '')
  me = dropbox.get('account/info')
  user_db = retrieve_user_from_dropbox(me.data)
  return auth.signin_user_db(user_db)


@dropbox.tokengetter
def get_dropbox_oauth_token():
  return flask.session.get('oauth_token')


@app.route('/signin/dropbox/')
def signin_dropbox():
  return auth.signin_oauth(dropbox, 'https')


def retrieve_user_from_dropbox(response):
  auth_id = 'dropbox_%s' % response['uid']
  user_db = model.User.get_by('auth_ids', auth_id)
  if user_db:
    return user_db

  return auth.create_user_db(
    auth_id=auth_id,
    name=response['display_name'],
    username=response['display_name'],
  )
