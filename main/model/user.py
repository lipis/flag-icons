# coding: utf-8

from __future__ import absolute_import

import hashlib

from google.appengine.ext import ndb

import model
import util


class User(model.Base):
  name = ndb.StringProperty(required=True)
  username = ndb.StringProperty(required=True)
  email = ndb.StringProperty(default='')
  auth_ids = ndb.StringProperty(repeated=True)
  active = ndb.BooleanProperty(default=True)
  admin = ndb.BooleanProperty(default=False)
  permissions = ndb.StringProperty(repeated=True)

  def has_permission(self, perm):
    return self.admin or perm in self.permissions

  def avatar_url_size(self, size=None):
    return '//gravatar.com/avatar/%(hash)s?d=identicon&r=x%(size)s' % {
        'hash': hashlib.md5(self.email or self.username).hexdigest(),
        'size': '&s=%d' % size if size > 0 else '',
      }
  avatar_url = property(avatar_url_size)

  _PROPERTIES = model.Base._PROPERTIES.union({
      'active',
      'admin',
      'auth_ids',
      'avatar_url',
      'email',
      'name',
      'username',
      'permissions',
    })

  @classmethod
  def get_dbs(cls, admin=None, active=None, permissions=None, **kwgs):
    return super(User, cls).get_dbs(
        admin=admin or util.param('admin', bool),
        active=active or util.param('active', bool),
        permissions=permissions or util.param('permissions', list),
        **kwgs
      )
