# coding: utf-8

import hashlib

from google.appengine.ext import ndb

import config
import util


class Base(ndb.Model):
  created = ndb.DateTimeProperty(auto_now_add=True)
  modified = ndb.DateTimeProperty(auto_now=True)
  version = ndb.IntegerProperty(default=config.CURRENT_VERSION_TIMESTAMP)

  _PROPERTIES = {
      'key',
      'id',
      'version',
      'created',
      'modified',
    }

  @classmethod
  def retrieve_one_by(cls, name, value):
    return cls.query(getattr(cls, name) == value).get()

  @classmethod
  def get_dbs(cls, query=None, order=None, limit=None, cursor=None, **kwgs):
    return util.retrieve_dbs(
        query or cls.query(),
        limit=limit or util.param('limit', int),
        cursor=cursor or util.param('cursor'),
        order=order or util.param('order') or '-created',
        **kwgs
      )


class Config(Base):
  analytics_id = ndb.StringProperty(default='')
  announcement_html = ndb.TextProperty(default='')
  announcement_type = ndb.StringProperty(default='info', choices=[
      'info', 'warning', 'success', 'danger',
    ])
  brand_name = ndb.StringProperty(default=config.APPLICATION_ID)
  facebook_app_id = ndb.StringProperty(default='')
  facebook_app_secret = ndb.StringProperty(default='')
  feedback_email = ndb.StringProperty(default='')
  flask_secret_key = ndb.StringProperty(default=util.uuid())
  notify_on_new_user = ndb.BooleanProperty(default=True)
  twitter_consumer_key = ndb.StringProperty(default='')
  twitter_consumer_secret = ndb.StringProperty(default='')

  @classmethod
  def get_master_db(cls):
    return cls.get_or_insert('master')

  @property
  def has_facebook(self):
    return bool(self.facebook_app_id and self.facebook_app_secret)

  @property
  def has_twitter(self):
    return bool(self.twitter_consumer_key and self.twitter_consumer_secret)

  _PROPERTIES = Base._PROPERTIES.union({
      'analytics_id',
      'announcement_html',
      'announcement_type',
      'brand_name',
      'facebook_app_id',
      'facebook_app_secret',
      'feedback_email',
      'flask_secret_key',
      'notify_on_new_user',
      'twitter_consumer_key',
      'twitter_consumer_secret',
    })


class User(Base):
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

  _PROPERTIES = Base._PROPERTIES.union({
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
  def get_dbs(cls, **kwgs):
    return super(User, cls).get_dbs(
        admin=util.param('admin', bool),
        active=util.param('active', bool),
        permissions=util.param('permissions', list),
        **kwgs
      )
