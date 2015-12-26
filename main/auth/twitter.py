# coding: utf-8

import flask

import auth
import config
import model
import util

from main import app

twitter_config = dict(
  access_token_url='https://api.twitter.com/oauth/access_token',
  authorize_url='https://api.twitter.com/oauth/authorize',
  base_url='https://api.twitter.com/1.1/',
  consumer_key=config.CONFIG_DB.twitter_consumer_key,
  consumer_secret=config.CONFIG_DB.twitter_consumer_secret,
  request_token_url='https://api.twitter.com/oauth/request_token',
)

twitter = auth.create_oauth_app(twitter_config, 'twitter')


@app.route('/api/auth/callback/twitter/')
def twitter_authorized():
  response = twitter.authorized_response()
  if response is None:
    flask.flash('You denied the request to sign in.')
    return flask.redirect(util.get_next_url())

  flask.session['oauth_token'] = (
    response['oauth_token'],
    response['oauth_token_secret'],
  )
  user_db = retrieve_user_from_twitter(response)
  return auth.signin_user_db(user_db)


@twitter.tokengetter
def get_twitter_token():
  return flask.session.get('oauth_token')


@app.route('/signin/twitter/')
def signin_twitter():
  return auth.signin_oauth(twitter)


def retrieve_user_from_twitter(response):
  auth_id = 'twitter_%s' % response['user_id']
  user_db = model.User.get_by('auth_ids', auth_id)
  return user_db or auth.create_user_db(
    auth_id=auth_id,
    name=response['screen_name'],
    username=response['screen_name'],
  )
