# coding: utf-8

from __future__ import absolute_import

from flask.ext import restful
import flask

from api import helpers
import auth
import model
import util

from main import api_v1


@api_v1.resource('/auth/signin/', endpoint='api.auth.signin')
class AuthAPI(restful.Resource):
  def post(self):
    username = util.param('username') or util.param('email')
    password = util.param('password')
    if not username or not password:
      return flask.abort(400)

    if username.find('@') > 0:
      user_db = model.User.get_by('email', username.lower())
    else:
      user_db = model.User.get_by('username', username.lower())

    if user_db and user_db.password_hash == util.password_hash(user_db, password):
      auth.signin_user_db(user_db)
      return helpers.make_response(user_db, model.User.FIELDS)
    return flask.abort(401)
