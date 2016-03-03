# coding: utf-8

import flask

import auth
import config
import model
import util

from main import app

vk_config = dict(
  access_token_url='https://oauth.vk.com/access_token',
  authorize_url='https://oauth.vk.com/authorize',
  base_url='https://api.vk.com/',
  consumer_key=config.CONFIG_DB.vk_app_id,
  consumer_secret=config.CONFIG_DB.vk_app_secret,
)

vk = auth.create_oauth_app(vk_config, 'vk')


@app.route('/api/auth/callback/vk/')
def vk_authorized():
  response = vk.authorized_response()
  if response is None:
    flask.flash(u'You denied the request to sign in.')
    return flask.redirect(util.get_next_url())

  access_token = response['access_token']
  flask.session['oauth_token'] = (access_token, '')
  me = vk.get(
    '/method/users.get',
    data={
      'access_token': access_token,
      'format': 'json',
    },
  )
  user_db = retrieve_user_from_vk(me.data['response'][0])
  return auth.signin_user_db(user_db)


@vk.tokengetter
def get_vk_oauth_token():
  return flask.session.get('oauth_token')


@app.route('/signin/vk/')
def signin_vk():
  return auth.signin_oauth(vk)


def retrieve_user_from_vk(response):
  auth_id = 'vk_%s' % response['uid']
  user_db = model.User.get_by('auth_ids', auth_id)
  if user_db:
    return user_db

  name = ' '.join((response['first_name'], response['last_name'])).strip()
  return auth.create_user_db(
    auth_id=auth_id,
    name=name,
    username=name,
  )
