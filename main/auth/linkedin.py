# coding: utf-8

import flask

import auth
import config
import model
import util

from main import app

linkedin_config = dict(
  access_token_method='POST',
  access_token_url='https://www.linkedin.com/uas/oauth2/accessToken',
  authorize_url='https://www.linkedin.com/uas/oauth2/authorization',
  base_url='https://api.linkedin.com/v1/',
  consumer_key=config.CONFIG_DB.linkedin_api_key,
  consumer_secret=config.CONFIG_DB.linkedin_secret_key,
  request_token_params={
    'scope': 'r_basicprofile r_emailaddress',
    'state': util.uuid(),
  },
)

linkedin = auth.create_oauth_app(linkedin_config, 'linkedin')


def change_linkedin_query(uri, headers, body):
  headers['x-li-format'] = 'json'
  return uri, headers, body


linkedin.pre_request = change_linkedin_query


@app.route('/api/auth/callback/linkedin/')
def linkedin_authorized():
  response = linkedin.authorized_response()
  if response is None:
    flask.flash('You denied the request to sign in.')
    return flask.redirect(util.get_next_url())

  flask.session['access_token'] = (response['access_token'], '')
  me = linkedin.get('people/~:(id,first-name,last-name,email-address)')
  user_db = retrieve_user_from_linkedin(me.data)
  return auth.signin_user_db(user_db)


@linkedin.tokengetter
def get_linkedin_oauth_token():
  return flask.session.get('access_token')


@app.route('/signin/linkedin/')
def signin_linkedin():
  return auth.signin_oauth(linkedin)


def retrieve_user_from_linkedin(response):
  auth_id = 'linkedin_%s' % response['id']
  user_db = model.User.get_by('auth_ids', auth_id)
  if user_db:
    return user_db

  names = [response.get('firstName', ''), response.get('lastName', '')]
  name = ' '.join(names).strip()
  email = response.get('emailAddress', '')
  return auth.create_user_db(
    auth_id=auth_id,
    name=name,
    username=email or name,
    email=email,
    verified=bool(email),
  )
