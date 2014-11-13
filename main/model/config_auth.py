# coding: utf-8

from __future__ import absolute_import

from google.appengine.ext import ndb


class ConfigAuth(object):
  facebook_app_id = ndb.StringProperty(default='')
  facebook_app_secret = ndb.StringProperty(default='')
  github_client_id = ndb.StringProperty(default='')
  github_client_secret = ndb.StringProperty(default='')
  twitter_consumer_key = ndb.StringProperty(default='')
  twitter_consumer_secret = ndb.StringProperty(default='')
  yahoo_consumer_key = ndb.StringProperty(default='')
  yahoo_consumer_secret = ndb.StringProperty(default='')

  @property
  def has_facebook(self):
    return bool(self.facebook_app_id and self.facebook_app_secret)

  @property
  def has_github(self):
    return bool(self.github_client_id and self.github_client_secret)

  @property
  def has_twitter(self):
    return bool(self.twitter_consumer_key and self.twitter_consumer_secret)

  @property
  def has_yahoo(self):
    return bool(self.yahoo_consumer_key and self.yahoo_consumer_secret)

  _PROPERTIES = {
      'facebook_app_id',
      'facebook_app_secret',
      'github_client_id',
      'github_client_secret',
      'twitter_consumer_key',
      'twitter_consumer_secret',
      'yahoo_consumer_key',
      'yahoo_consumer_secret',
    }
