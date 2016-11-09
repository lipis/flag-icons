# coding: utf-8

import flask
import jwt

import auth
import config
import util

from main import app


azure_ad_config = dict(
  access_token_method='POST',
  access_token_url='https://login.microsoftonline.com/common/oauth2/token',
  authorize_url='https://login.microsoftonline.com/common/oauth2/authorize',
  base_url='',
  consumer_key=config.CONFIG_DB.azure_ad_client_id,
  consumer_secret=config.CONFIG_DB.azure_ad_client_secret,
  request_token_params={
    'scope': 'openid profile user_impersonation',
  },
)

azure_ad = auth.create_oauth_app(azure_ad_config, 'azure_ad')


@app.route('/api/auth/callback/azure_ad/')
def azure_ad_authorized():
  response = azure_ad.authorized_response()
  print response
  if response is None:
    flask.flash('You denied the request to sign in.')
    return flask.redirect(util.get_next_url)
  id_token = response['id_token']
  flask.session['oauth_token'] = (id_token, '')
  try:
    decoded_id_token = jwt.decode(id_token, verify=False)
  except (jwt.DecodeError, jwt.ExpiredSignature):
    flask.flash('You denied the request to sign in.')
    return flask.redirect(util.get_next_url)
  user_db = retrieve_user_from_azure_ad(decoded_id_token)
  return auth.signin_user_db(user_db)


@azure_ad.tokengetter
def get_azure_ad_oauth_token():
  return flask.session.get('oauth_token')


@app.route('/signin/azure_ad/')
def signin_azure_ad():
  return auth.signin_oauth(azure_ad)


def retrieve_user_from_azure_ad(response):
  auth_id = 'azure_ad_%s' % response['oid']
  email = response.get('upn', '')
  first_name = response.get('given_name', '')
  last_name = response.get('family_name', '')
  username = ' '.join((first_name, last_name)).strip()
  return auth.create_user_db(
    auth_id=auth_id,
    name='%s %s' % (first_name, last_name),
    username=email or username,
    email=email,
    verified=bool(email),
  )
