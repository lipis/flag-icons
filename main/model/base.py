# coding: utf-8

from __future__ import absolute_import

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
  def get_by(cls, name, value):
    return cls.query(getattr(cls, name) == value).get()

  @classmethod
  def get_dbs(cls, query=None, ancestor=None, order=None, limit=None, cursor=None, **kwargs):
    return util.get_dbs(
        query or cls.query(ancestor=ancestor),
        limit=limit or util.param('limit', int),
        cursor=cursor or util.param('cursor'),
        order=order or util.param('order') or '-created',
        **kwargs
      )
