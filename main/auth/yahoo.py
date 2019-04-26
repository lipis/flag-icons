# coding: utf-8

from __future__ import absolute_import

import base64
import flask

from flask_oauthlib import client
from werkzeug import urls

import auth
import config
import model
import util

from main import app


yahoo_config = dict(
  access_token_method='POST',
  access_token_params={'grant_type': 'authorization_code'},
  access_token_url='https://api.login.yahoo.com/oauth2/get_token',
  authorize_url='https://api.login.yahoo.com/oauth2/request_auth',
  base_url='https://social.yahooapis.com/v1/user/',
  consumer_key=config.CONFIG_DB.yahoo_consumer_key,
  consumer_secret=config.CONFIG_DB.yahoo_consumer_secret,
  request_token_params={'state': util.uuid()},
)

yahoo = auth.create_oauth_app(yahoo_config, 'yahoo')


def yahoo_handle_oauth2_response(args):
  access_args = {
    'code': args.get('code'),
    'client_id': yahoo.consumer_key,
    'client_secret': yahoo.consumer_secret,
    'redirect_uri': flask.session.get('%s_oauthredir' % yahoo.name),
    'state': args.get('state'),
  }
  access_args.update(yahoo.access_token_params)
  auth_header = 'Basic %s' % base64.b64encode(
    ('%s:%s' % (yahoo.consumer_key, yahoo.consumer_secret)).encode('latin1')
  ).strip().decode('latin1')
  response, content = yahoo.http_request(
    yahoo.expand_url(yahoo.access_token_url),
    method=yahoo.access_token_method,
    data=urls.url_encode(access_args),
    headers={
      'Authorization': auth_header,
      'User-Agent': config.USER_AGENT,
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  )
  data = client.parse_response(response, content)
  if response.code not in (200, 201):
    raise client.OAuthException(
      'Invalid response from %s' % yahoo.name,
      type='invalid_response', data=data,
    )
  return data


yahoo.handle_oauth2_response = yahoo_handle_oauth2_response


@app.route('/api/auth/callback/yahoo/')
def yahoo_authorized():
  response = yahoo.authorized_response()
  if response is None or flask.request.args.get('error'):
    flask.flash('You denied the request to sign in.')
    return flask.redirect(util.get_next_url())

  flask.session['oauth_token'] = (response['access_token'], '')
  yahoo_guid = response['xoauth_yahoo_guid']
  me = yahoo.get('%s/profile' % yahoo_guid, data={'format': 'json'})
  user_db = retrieve_user_from_yahoo(me.data['profile'])
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

  username = response.get('nickname', '').strip()
  names = [response.get('givenName', ''), response.get('familyName', '')]
  name = ' '.join(names).strip() or username
  if not name:
    name = 'yahoo_user_%s' % response['guid']

  emails = response.get('emails', {})
  if not isinstance(emails, list):
    emails = [emails]
  emails = [e for e in emails if 'handle' in e]
  emails.sort(key=lambda e: e.get('primary', False))
  email = emails[0]['handle'] if emails else ''

  return auth.create_user_db(
    auth_id=auth_id,
    name=name,
    username=username,
    email=email,
    verified=bool(email),
  )
