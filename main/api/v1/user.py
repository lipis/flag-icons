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

    user_dbs, user_cursor = model.User.get_dbs()
    return helpers.make_response(user_dbs, model.User.FIELDS, user_cursor)

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


@api.resource('/api/v1/user/<string:user_key>/', endpoint='api.user')
class UserAPI(restful.Resource):
  @auth.admin_required
  def get(self, user_key):
    user_db = ndb.Key(urlsafe=user_key).get()
    if not user_db:
      helpers.make_not_found_exception('User %s not found' % user_key)
    return helpers.make_response(user_db, model.User.FIELDS)

  @auth.admin_required
  def delete(self, user_key):
    user_db = ndb.Key(urlsafe=user_key).get()
    if not user_db:
      helpers.make_not_found_exception('User %s not found' % user_key)
    user_db.key.delete()
    return helpers.make_response(user_db, model.User.FIELDS)


###############################################################################
# Helpers
###############################################################################
@ndb.transactional(xg=True)
def delete_user_dbs(user_db_keys):
  ndb.delete_multi(user_db_keys)
