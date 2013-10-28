# -*- coding: utf-8 -*-

import hashlib


class BaseX(object):
  @classmethod
  def retrieve_one_by(cls, name, value):
    cls_db_list = cls.query(getattr(cls, name) == value).fetch(1)
    if cls_db_list:
      return cls_db_list[0]
    return None


class ConfigX(object):
  @classmethod
  def get_master_db(cls):
    return cls.get_or_insert('master')


class UserX(object):
  @property
  def avatar_url(self, size=80):
    return '//gravatar.com/avatar/%s?d=identicon&r=x&s=%d' % (
        hashlib.md5((self.email or self.name).encode('utf-8')).hexdigest().lower(),
        size
      )
