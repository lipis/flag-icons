# coding: utf-8

from __future__ import absolute_import

from google.appengine.ext import ndb


class ConfigAuth(object):
  dropbox_app_key = ndb.StringProperty(default='')
  dropbox_app_secret = ndb.StringProperty(default='')
  facebook_app_id = ndb.StringProperty(default='')
  facebook_app_secret = ndb.StringProperty(default='')
  github_client_id = ndb.StringProperty(default='')
  github_client_secret = ndb.StringProperty(default='')
  microsoft_client_id = ndb.StringProperty(default='')
  microsoft_client_secret = ndb.StringProperty(default='')
  twitter_consumer_key = ndb.StringProperty(default='')
  twitter_consumer_secret = ndb.StringProperty(default='')

  @property
  def has_dropbox(self):
    return bool(self.dropbox_app_key and self.dropbox_app_secret)

  @property
  def has_facebook(self):
    return bool(self.facebook_app_id and self.facebook_app_secret)

  @property
  def has_github(self):
    return bool(self.github_client_id and self.github_client_secret)

  @property
  def has_microsoft(self):
    return bool(self.microsoft_client_id and self.microsoft_client_secret)

  @property
  def has_twitter(self):
    return bool(self.twitter_consumer_key and self.twitter_consumer_secret)

  _PROPERTIES = {
      'dropbox_app_key',
      'dropbox_app_secret',
      'facebook_app_id',
      'facebook_app_secret',
      'github_client_id',
      'github_client_secret',
      'microsoft_client_id',
      'microsoft_client_secret',
      'twitter_consumer_key',
      'twitter_consumer_secret',
    }
