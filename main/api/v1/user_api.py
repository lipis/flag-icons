# coding: utf-8

from google.appengine.ext import ndb
from flask.ext import restful
import flask

from api import helpers
import auth
import model
import util

from main import api


@api.resource('/api/v1/users/', endpoint='api.users')
class UsersAPI(restful.Resource):
  @auth.admin_required
  def get(self):
    user_keys = util.param('user_keys', list)
    if user_keys:
      user_db_keys = [ndb.Key(urlsafe=k) for k in user_keys]
      user_dbs = ndb.get_multi(user_db_keys)
      return helpers.make_response(user_dbs, model.User.FIELDS)

    user_dbs, next_cursor = model.User.get_dbs()
    return helpers.make_response(user_dbs, model.User.FIELDS, next_cursor)

  @auth.admin_required
  def delete(self):
    user_keys = util.param('user_keys', list)
    if not user_keys:
      helpers.make_not_found_exception('User(s) %s not found' % user_keys)
    user_db_keys = [ndb.Key(urlsafe=k) for k in user_keys]
    delete_user_dbs(user_db_keys)
    return flask.jsonify({
        'result': user_keys,
        'status': 'success',
      })


@api.resource('/api/v1/user/<string:key>/', endpoint='api.user')
class UserAPI(restful.Resource):
  @auth.admin_required
  def get(self, key):
    user_db = ndb.Key(urlsafe=key).get()
    if not user_db:
      helpers.make_not_found_exception('User %s not found' % key)
    return helpers.make_response(user_db, model.User.FIELDS)

  @auth.admin_required
  def delete(self, key):
    user_db = ndb.Key(urlsafe=key).get()
    if not user_db:
      helpers.make_not_found_exception('User %s not found' % key)
    user_db.key.delete()
    return flask.jsonify({
        'result': key,
        'status': 'success',
      })


###############################################################################
# Helpers
###############################################################################
@ndb.transactional(xg=True)
def delete_user_dbs(user_db_keys):
  ndb.delete_multi(user_db_keys)
