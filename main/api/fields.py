# coding: utf-8

import urllib

from flask_restful import fields
from flask_restful.fields import *


class BlobKey(fields.Raw):
  def format(self, value):
    return urllib.quote(str(value))


class Blob(fields.Raw):
  def format(self, value):
    return repr(value)


class DateTime(fields.DateTime):
  def format(self, value):
    return value.isoformat()


class GeoPt(fields.Raw):
  def format(self, value):
    return '%s,%s' % (value.lat, value.lon)


class Id(fields.Raw):
  def output(self, key, obj):
    try:
      value = getattr(obj, 'key', None).id()
      return super(Id, self).output(key, {'id': value})
    except AttributeError:
      return None


class Integer(fields.Integer):
  def format(self, value):
    if value > 9007199254740992 or value < -9007199254740992:
      return str(value)
    return value


class Key(fields.Raw):
  def format(self, value):
    return value.urlsafe()
