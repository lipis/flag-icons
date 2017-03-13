# coding: utf-8

from __future__ import absolute_import

import hashlib

from google.appengine.ext import ndb
from webargs.flaskparser import parser
from webargs import fields as wf

from api import fields
import model
import util
import config


class User(model.Base):
  name = ndb.StringProperty(required=True)
  username = ndb.StringProperty(required=True)
  email = ndb.StringProperty(default='')
  auth_ids = ndb.StringProperty(repeated=True)
  active = ndb.BooleanProperty(default=True)
  admin = ndb.BooleanProperty(default=False)
  permissions = ndb.StringProperty(repeated=True)
  verified = ndb.BooleanProperty(default=False)
  token = ndb.StringProperty(default='')
  password_hash = ndb.StringProperty(default='')

  def has_permission(self, perm):
    return self.admin or perm in self.permissions

  def has_facebook(self):
    for auth_id in self.auth_ids:
      if auth_id.startswith('facebook'):
        return auth_id
    return None

  def avatar_url_size(self, size=None):
    facebook_id = self.has_facebook()
    if facebook_id:
      return '//graph.facebook.com/%(id)s/picture%(size)s' % {
        'id': facebook_id.split('_')[1],
        'size': '?width=%s&height=%s' % (size, size) if size else '',
      }

    return '//gravatar.com/avatar/%(hash)s?d=identicon&r=x%(size)s' % {
      'hash': hashlib.md5(
        (self.email or self.username).encode('utf-8')).hexdigest(),
      'size': '&s=%d' % size if size > 0 else '',
    }

  avatar_url = property(avatar_url_size)

  @classmethod
  def get_dbs(
    cls, admin=None, active=None, verified=None, permissions=None, **kwargs
  ):
    args = parser.parse({
      'admin': wf.Bool(missing=None),
      'active': wf.Bool(missing=None),
      'verified': wf.Bool(missing=None),
      'permissions': wf.DelimitedList(wf.Str(), delimiter=',', missing=[]),
    })
    return super(User, cls).get_dbs(
      admin=admin or args['admin'],
      active=active or args['active'],
      verified=verified or args['verified'],
      permissions=permissions or args['permissions'],
      **kwargs
    )

  @classmethod
  def is_username_available(cls, username, self_key=None):
    if self_key is None:
      return cls.get_by('username', username) is None
    user_keys, _ = util.get_keys(cls.query(), username=username, limit=2)
    return not user_keys or self_key in user_keys and not user_keys[1:]

  @classmethod
  def is_email_available(cls, email, self_key=None):
    if not config.CONFIG_DB.check_unique_email:
      return True
    user_keys, _ = util.get_keys(
      cls.query(), email=email, verified=True, limit=2,
    )
    return not user_keys or self_key in user_keys and not user_keys[1:]

  FIELDS = {
    'active': fields.Boolean,
    'admin': fields.Boolean,
    'auth_ids': fields.List(fields.String),
    'avatar_url': fields.String,
    'email': fields.String,
    'name': fields.String,
    'permissions': fields.List(fields.String),
    'username': fields.String,
    'verified': fields.Boolean,
  }

  FIELDS.update(model.Base.FIELDS)
