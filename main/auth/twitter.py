# coding: utf-8

import flask

import config
import model
import util
import auth

from main import app


twitter_config = dict(
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authorize',
    consumer_key=config.CONFIG_DB.twitter_consumer_key,
    consumer_secret=config.CONFIG_DB.twitter_consumer_secret,
  )

twitter = auth.create_oauth_app(twitter_config, 'twitter')


@app.route('/_s/callback/twitter/oauth-authorized/')
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
  try:
    return auth.signin_oauth(twitter)
  except:
    flask.flash(
        'Something went wrong with Twitter sign in. Please try again.',
        category='danger',
      )
    return flask.redirect(flask.url_for('signin', next=util.get_next_url()))


def retrieve_user_from_twitter(response):
  auth_id = 'twitter_%s' % response['user_id']
  user_db = model.User.get_by('auth_ids', auth_id)
  return user_db or auth.create_user_db(
      auth_id=auth_id,
      name=response['screen_name'],
      username=response['screen_name'],
    )
