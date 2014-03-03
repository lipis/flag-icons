# -*- coding: utf-8 -*-

import hashlib


class BaseX(object):
  @classmethod
  def retrieve_one_by(cls, name, value):
    return cls.query(getattr(cls, name) == value).get()


class ConfigX(object):
  @classmethod
  def get_master_db(cls):
    return cls.get_or_insert('master')

  @property
  def has_facebook(self):
    return bool(self.facebook_app_id and self.facebook_app_secret)

  @property
  def has_twitter(self):
    return bool(self.twitter_consumer_key and self.twitter_consumer_secret)


class UserX(object):
  def has_permission(self, perm):
    return self.admin or perm in self.permissions

  def avatar_url_size(self, size=None):
    return '//gravatar.com/avatar/%(hash)s?d=identicon&r=x%(size)s' % {
        'hash': hashlib.md5(self.email or self.username).hexdigest(),
        'size': '&s=%d' % size if size > 0 else '',
      }
  avatar_url = property(avatar_url_size)
