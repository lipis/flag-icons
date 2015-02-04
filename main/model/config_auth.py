# coding: utf-8

from __future__ import absolute_import

from google.appengine.ext import ndb


class ConfigAuth(object):
  bitbucket_key = ndb.StringProperty(default='')
  bitbucket_secret = ndb.StringProperty(default='')
  dropbox_app_key = ndb.StringProperty(default='')
  dropbox_app_secret = ndb.StringProperty(default='')
  facebook_app_id = ndb.StringProperty(default='')
  facebook_app_secret = ndb.StringProperty(default='')
  github_client_id = ndb.StringProperty(default='')
  github_client_secret = ndb.StringProperty(default='')
  instagram_client_id = ndb.StringProperty(default='')
  instagram_client_secret = ndb.StringProperty(default='')
  linkedin_api_key = ndb.StringProperty(default='')
  linkedin_secret_key = ndb.StringProperty(default='')
  microsoft_client_id = ndb.StringProperty(default='')
  microsoft_client_secret = ndb.StringProperty(default='')
  twitter_consumer_key = ndb.StringProperty(default='')
  twitter_consumer_secret = ndb.StringProperty(default='')
  yahoo_consumer_key = ndb.StringProperty(default='')
  yahoo_consumer_secret = ndb.StringProperty(default='')

  @property
  def has_bitbucket(self):
    return bool(self.bitbucket_key and self.bitbucket_secret)

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
  def has_instagram(self):
    return bool(self.instagram_client_id and self.instagram_client_secret)

  @property
  def has_linkedin(self):
    return bool(self.linkedin_api_key and self.linkedin_secret_key)

  @property
  def has_microsoft(self):
    return bool(self.microsoft_client_id and self.microsoft_client_secret)

  @property
  def has_twitter(self):
    return bool(self.twitter_consumer_key and self.twitter_consumer_secret)

  @property
  def has_yahoo(self):
    return bool(self.yahoo_consumer_key and self.yahoo_consumer_secret)

  _PROPERTIES = {
      'bitbucket_key',
      'bitbucket_secret',
      'dropbox_app_key',
      'dropbox_app_secret',
      'facebook_app_id',
      'facebook_app_secret',
      'github_client_id',
      'github_client_secret',
      'instagram_client_id',
      'instagram_client_secret',
      'linkedin_api_key',
      'linkedin_secret_key',
      'microsoft_client_id',
      'microsoft_client_secret',
      'twitter_consumer_key',
      'twitter_consumer_secret',
      'yahoo_consumer_key',
      'yahoo_consumer_secret',
    }
