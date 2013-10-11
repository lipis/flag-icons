# -*- coding: utf-8 -*-

from google.appengine.ext import ndb
from uuid import uuid4
import os
import modelx


# The timestamp of the currently deployed version
TIMESTAMP = long(os.environ.get('CURRENT_VERSION_ID').split('.')[1]) >> 28


class Base(ndb.Model, modelx.BaseX):
  created = ndb.DateTimeProperty(auto_now_add=True)
  modified = ndb.DateTimeProperty(auto_now=True)
  version = ndb.IntegerProperty(default=TIMESTAMP)
  _PROPERTIES = set([
      'key',
      'id',
      'version',
      'created',
      'modified',
    ])


class Config(Base, modelx.ConfigX):
  analytics_id = ndb.StringProperty(default='')
  announcement_html = ndb.StringProperty(default='')
  announcement_type = ndb.StringProperty(default='info', choices=[
      'info', 'warning', 'success', 'danger',
    ])
  brand_name = ndb.StringProperty(default='gae-init')
  facebook_app_id = ndb.StringProperty(default='')
  facebook_app_secret = ndb.StringProperty(default='')
  feedback_email = ndb.StringProperty(default='')
  flask_secret_key = ndb.StringProperty(default=str(uuid4()).replace('-', ''))
  github_client_id = ndb.StringProperty(default='')
  github_client_secret = ndb.StringProperty(default='')
  twitter_consumer_key = ndb.StringProperty(default='')
  twitter_consumer_secret = ndb.StringProperty(default='')

  _PROPERTIES = Base._PROPERTIES.union(set([
      'analytics_id',
      'announcement_html',
      'announcement_type',
      'brand_name',
      'facebook_app_id',
      'facebook_app_secret',
      'feedback_email',
      'flask_secret_key',
      'github_client_id',
      'github_client_secret',
      'twitter_consumer_key',
      'twitter_consumer_secret'
    ]))


class User(Base, modelx.UserX):
  name = ndb.StringProperty(indexed=True, required=True)
  username = ndb.StringProperty(indexed=True, required=True)
  email = ndb.StringProperty(indexed=True, default='')

  active = ndb.BooleanProperty(default=True)
  admin = ndb.BooleanProperty(default=False)

  federated_id = ndb.StringProperty(indexed=True, default='')
  facebook_id = ndb.StringProperty(indexed=True, default='')
  twitter_id = ndb.StringProperty(indexed=True, default='')
  github_id = ndb.StringProperty(indexed=True, default='')

  _PROPERTIES = Base._PROPERTIES.union(set([
      'name',
      'username',
      'avatar_url',
    ]))
