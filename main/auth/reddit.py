# coding: utf-8

import base64

from flask.ext.oauthlib import client
from werkzeug import urls
import flask

import auth
import config
import model
import util

from main import app


reddit_config = dict(
    access_token_method='POST',
    access_token_params={'grant_type': 'authorization_code'},
    access_token_url='https://ssl.reddit.com/api/v1/access_token',
    authorize_url='https://ssl.reddit.com/api/v1/authorize',
    base_url='https://oauth.reddit.com/api/v1/',
    consumer_key=model.Config.get_master_db().reddit_client_id,
    consumer_secret=model.Config.get_master_db().reddit_client_secret,
    request_token_params={'scope': 'identity', 'state': util.uuid()},
  )

reddit = auth.create_oauth_app(reddit_config, 'reddit')


def reddit_handle_oauth2_response():
  access_args = {
      'code': flask.request.args.get('code'),
      'client_id': reddit.consumer_key,
      'redirect_uri': flask.session.get('%s_oauthredir' % reddit.name),
    }
  access_args.update(reddit.access_token_params)
  auth_header = 'Basic %s' % base64.b64encode(
      ('%s:%s' % (reddit.consumer_key, reddit.consumer_secret)).encode('latin1')
    ).strip().decode('latin1')
  response, content = reddit.http_request(
      reddit.expand_url(reddit.access_token_url),
      method=reddit.access_token_method,
      data=urls.url_encode(access_args),
      headers={
          'Authorization': auth_header,
          'User-Agent': config.USER_AGENT,
        },
    )
  data = client.parse_response(response, content)
  if response.code not in (200, 201):
    raise client.OAuthException(
        'Invalid response from %s' % reddit.name,
        type='invalid_response', data=data,
      )
  return data


reddit.handle_oauth2_response = reddit_handle_oauth2_response


@app.route('/api/auth/callback/reddit/')
def reddit_authorized():
  response = reddit.authorized_response()
  if response is None or flask.request.args.get('error'):
    flask.flash('You denied the request to sign in.')
    return flask.redirect(util.get_next_url())

  flask.session['oauth_token'] = (response['access_token'], '')
  me = reddit.request('me')
  user_db = retrieve_user_from_reddit(me.data)
  return auth.signin_user_db(user_db)


@reddit.tokengetter
def get_reddit_oauth_token():
  return flask.session.get('oauth_token')


@app.route('/signin/reddit/')
def signin_reddit():
  return auth.signin_oauth(reddit)


def retrieve_user_from_reddit(response):
  auth_id = 'reddit_%s' % response['id']
  user_db = model.User.get_by('auth_ids', auth_id)
  if user_db:
    return user_db

  return auth.create_user_db(
      auth_id=auth_id,
      name=response['name'],
      username=response['name'],
    )
