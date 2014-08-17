# coding: utf-8

import urllib

from flask.ext.restful import fields


class BlobKey(fields.Raw):
  def format(self, value):
    return urllib.quote(str(value))


class Blob(fields.Raw):
  def format(self, value):
    return repr(value)


class DateTimeField(fields.Raw):
  def format(self, value):
    return value.isoformat()


class GeoPtField(fields.Raw):
  def format(self, value):
    return '%s,%s' % (value.lat, value.lon)


class IdField(fields.Raw):
  def output(self, key, obj):
    try:
      value = getattr(obj, 'key', None).id()
      return super(IdField, self).output(key, {'id': value})
    except AttributeError:
      return None


class IntegerField(fields.Raw):
  def format(self, value):
    if value > 9007199254740992 or value < -9007199254740992:
      return repr(value)
    return value


class KeyField(fields.Raw):
  def format(self, value):
    return value.urlsafe()
