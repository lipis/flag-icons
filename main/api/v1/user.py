# coding: utf-8

from __future__ import absolute_import

from google.appengine.ext import ndb
from flask.ext import restful
import flask

from api import helpers
import auth
import model
import util

from main import api_v1


@api_v1.resource('/admin/user/', endpoint='api.admin.user.list')
class AdminUserListAPI(restful.Resource):
  @auth.admin_required
  def get(self):
    user_keys = util.param('user_keys', list)
    if user_keys:
      user_db_keys = [ndb.Key(urlsafe=k) for k in user_keys]
      user_dbs = ndb.get_multi(user_db_keys)
      return helpers.make_response(user_dbs, model.User.FIELDS)

    user_dbs, cursors = model.User.get_dbs(prev_cursor=True)
    return helpers.make_response(user_dbs, model.User.FIELDS, cursors)

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


@api_v1.resource('/admin/user/<string:user_key>/', endpoint='api.admin.user')
class AdminUserAPI(restful.Resource):
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
    delete_user_dbs([user_db.key])
    return helpers.make_response(user_db, model.User.FIELDS)


###############################################################################
# Helpers
###############################################################################
@ndb.transactional(xg=True)
def delete_user_dbs(user_db_keys):
  ndb.delete_multi(user_db_keys)
