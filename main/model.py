import os
from google.appengine.ext import ndb
import modelx


class Base(ndb.Model, modelx.BaseX):
  created = ndb.DateTimeProperty(auto_now_add=True)
  modified = ndb.DateTimeProperty(auto_now=True)
  _PROPERTIES = set([
      'key', 'id', 'created', 'modified', 'created_ago', 'modified_ago',
    ])


class Config(Base, modelx.ConfigX):
  brand_name = ndb.StringProperty(default='GAE Init')
  analytics_id = ndb.StringProperty(default='')
  facebook_app_id = ndb.StringProperty(default='')
  facebook_app_secret = ndb.StringProperty(default='')
  twitter_consumer_key = ndb.StringProperty(default='')
  twitter_consumer_secret = ndb.StringProperty(default='')
  flask_secret_key = ndb.StringProperty(default='%r' % os.urandom(24))
  _PROPERTIES = Base._PROPERTIES.union(set([
      'brand_name',
      'analytics_id',
      'facebook_app_id',
      'facebook_app_secret',
      'twitter_consumer_key',
      'twitter_consumer_secret',
      'flask_secret_key',
    ]))


class User(Base, modelx.UserX):
  name = ndb.StringProperty(indexed=True, required=True)
  username = ndb.StringProperty(indexed=True, required=True)
  email = ndb.StringProperty(default='')

  active = ndb.BooleanProperty(default=True)
  admin = ndb.BooleanProperty(default=False)

  federated_id = ndb.StringProperty(default='')
  facebook_id = ndb.StringProperty(default='')
  twitter_id = ndb.StringProperty(default='')

  _PROPERTIES = Base._PROPERTIES.union(set([
      'name', 'username', 'avatar_url',
    ]))
