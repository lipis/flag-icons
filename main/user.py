# -*- coding: utf-8 -*-

from flask.ext import wtf
from google.appengine.ext import ndb
import flask

import auth
import model
import util

from main import app


###############################################################################
# User List
###############################################################################
@app.route('/_s/user/', endpoint='user_list_service')
@app.route('/user/')
@auth.admin_required
def user_list():
  user_dbs, more_cursor = util.retrieve_dbs(
      model.User.query(),
      limit=util.param('limit', int),
      cursor=util.param('cursor'),
      order=util.param('order') or '-created',
      name=util.param('name'),
      admin=util.param('admin', bool),
    )

  if flask.request.path.startswith('/_s/'):
    return util.jsonify_model_dbs(user_dbs, more_cursor)

  return flask.render_template(
      'user/user_list.html',
      html_class='user-list',
      title='User List',
      user_dbs=user_dbs,
      more_url=util.generate_more_url(more_cursor),
      has_json=True,
    )


###############################################################################
# User Update
###############################################################################
class UserUpdateForm(wtf.Form):
  username = wtf.StringField('Username',
      [wtf.validators.required(), wtf.validators.length(min=3)],
      filters=[util.email_filter],
    )
  name = wtf.StringField('Name',
      [wtf.validators.required()], filters=[util.strip_filter],
    )
  email = wtf.StringField('Email',
      [wtf.validators.optional(), wtf.validators.email()],
      filters=[util.email_filter],
    )
  admin = wtf.BooleanField('Admin')
  active = wtf.BooleanField('Active')


@app.route('/user/<int:user_id>/update/', methods=['GET', 'POST'])
@auth.admin_required
def user_update(user_id):
  user_db = model.User.get_by_id(user_id)
  if not user_db:
    flask.abort(404)

  form = UserUpdateForm(obj=user_db)
  if form.validate_on_submit():
    if not util.is_valid_username(form.username.data):
      form.username.errors.append('This username is invalid.')
    elif not is_username_available(form.username.data, user_db):
      form.username.errors.append('This username is taken.')
    else:
      form.populate_obj(user_db)
      if auth.current_user_id() == user_db.key.id():
        user_db.admin = True
        user_db.active = True
      user_db.put()
      return flask.redirect(flask.url_for('user_list', order='-modified'))

  if flask.request.path.startswith('/_s/'):
    return util.jsonify_model_db(user_db)

  return flask.render_template(
      'user/user_update.html',
      title=user_db.name,
      html_class='user-update',
      form=form,
      user_db=user_db,
    )


###############################################################################
# User Delete
###############################################################################
@app.route('/_s/user/delete/', methods=['DELETE'])
@auth.admin_required
def user_delete_service():
  user_keys = util.param('user_keys', list)
  user_db_keys = [ndb.Key(urlsafe=k) for k in user_keys]
  delete_user_dbs(user_db_keys)
  return flask.jsonify({
      'result': user_keys,
      'status': 'success',
    })


@ndb.transactional(xg=True)
def delete_user_dbs(user_db_keys):
  ndb.delete_multi(user_db_keys)


###############################################################################
# Helpers
###############################################################################
def is_username_available(username, self_db=None):
  user_dbs, more_cursor = util.retrieve_dbs(
      model.User.query(),
      username=username,
      limit=2,
    )
  c = len(user_dbs)
  return not (c == 2 or c == 1 and self_db and self_db.key != user_dbs[0].key)
