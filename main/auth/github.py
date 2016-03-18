# coding: utf-8

import flask

import auth
import config
import model
import util

from main import app

github_config = dict(
  access_token_method='POST',
  access_token_url='https://github.com/login/oauth/access_token',
  authorize_url='https://github.com/login/oauth/authorize',
  base_url='https://api.github.com/',
  consumer_key=config.CONFIG_DB.github_client_id,
  consumer_secret=config.CONFIG_DB.github_client_secret,
  request_token_params={'scope': 'user:email'},
)

github = auth.create_oauth_app(github_config, 'github')


@app.route('/api/auth/callback/github/')
def github_authorized():
  response = github.authorized_response()
  if response is None:
    flask.flash('You denied the request to sign in.')
    return flask.redirect(util.get_next_url())
  flask.session['oauth_token'] = (response['access_token'], '')
  me = github.get('user')
  user_db = retrieve_user_from_github(me.data)
  return auth.signin_user_db(user_db)


@github.tokengetter
def get_github_oauth_token():
  return flask.session.get('oauth_token')


@app.route('/signin/github/')
def signin_github():
  return auth.signin_oauth(github)


def retrieve_user_from_github(response):
  auth_id = 'github_%s' % str(response['id'])
  user_db = model.User.get_by('auth_ids', auth_id)
  return user_db or auth.create_user_db(
    auth_id=auth_id,
    name=response['name'] or response['login'],
    username=response['login'],
    email=response.get('email', ''),
    verified=bool(response.get('email', '')),
  )
