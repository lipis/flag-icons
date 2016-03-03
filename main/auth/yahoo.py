# coding: utf-8

import flask

import auth
import model
import util

from main import app

yahoo_config = dict(
  access_token_url='https://api.login.yahoo.com/oauth/v2/get_token',
  authorize_url='https://api.login.yahoo.com/oauth/v2/request_auth',
  base_url='https://query.yahooapis.com/',
  consumer_key=model.Config.get_master_db().yahoo_consumer_key,
  consumer_secret=model.Config.get_master_db().yahoo_consumer_secret,
  request_token_url='https://api.login.yahoo.com/oauth/v2/get_request_token',
)

yahoo = auth.create_oauth_app(yahoo_config, 'yahoo')


@app.route('/api/auth/callback/yahoo/')
def yahoo_authorized():
  response = yahoo.authorized_response()
  if response is None:
    flask.flash('You denied the request to sign in.')
    return flask.redirect(util.get_next_url())

  flask.session['oauth_token'] = (
    response['oauth_token'],
    response['oauth_token_secret'],
  )

  fields = 'guid, emails, familyName, givenName, nickname'
  me = yahoo.get(
    '/v1/yql',
    data={
      'format': 'json',
      'q': 'select %s from social.profile where guid = me;' % fields,
      'realm': 'yahooapis.com',
    },
  )
  user_db = retrieve_user_from_yahoo(me.data['query']['results']['profile'])
  return auth.signin_user_db(user_db)


@yahoo.tokengetter
def get_yahoo_oauth_token():
  return flask.session.get('oauth_token')


@app.route('/signin/yahoo/')
def signin_yahoo():
  return auth.signin_oauth(yahoo)


def retrieve_user_from_yahoo(response):
  auth_id = 'yahoo_%s' % response['guid']
  user_db = model.User.get_by('auth_ids', auth_id)
  if user_db:
    return user_db

  names = [response.get('givenName', ''), response.get('familyName', '')]
  emails = response.get('emails', {})
  if not isinstance(emails, list):
    emails = [emails]
  emails = [e for e in emails if 'handle' in e]
  emails.sort(key=lambda e: e.get('primary', False))
  email = emails[0]['handle'] if emails else ''
  return auth.create_user_db(
    auth_id=auth_id,
    name=' '.join(names).strip() or response['nickname'],
    username=response['nickname'],
    email=email,
    verified=bool(email),
  )
