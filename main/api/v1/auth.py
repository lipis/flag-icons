# coding: utf-8

from __future__ import absolute_import

from webargs.flaskparser import parser
from webargs import fields as wf
import flask
import flask_restful

from api import helpers
import auth
import model
import util

from main import api_v1


@api_v1.resource('/auth/signin/', endpoint='api.auth.signin')
class AuthAPI(flask_restful.Resource):
  def post(self):
    args = parser.parse({
      'username': wf.Str(missing=None),
      'email': wf.Str(missing=None),
      'password': wf.Str(missing=None),
    })
    handler = args['username'] or args['email']
    password = args['password']
    if not handler or not password:
      return flask.abort(400)

    user_db = model.User.get_by(
      'email' if '@' in handler else 'username', handler.lower()
    )

    if user_db and user_db.password_hash == util.password_hash(user_db, password):
      auth.signin_user_db(user_db)
      return helpers.make_response(user_db, model.User.FIELDS)
    return flask.abort(401)
