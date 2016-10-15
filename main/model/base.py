# coding: utf-8

from __future__ import absolute_import

from google.appengine.ext import ndb
from marshmallow import validate
from webargs.flaskparser import parser
from webargs import fields as wf

from api import fields
import config
import util


class Base(ndb.Model):
  created = ndb.DateTimeProperty(auto_now_add=True)
  modified = ndb.DateTimeProperty(auto_now=True)
  version = ndb.IntegerProperty(default=config.CURRENT_VERSION_TIMESTAMP)

  @classmethod
  def get_by(cls, name, value):
    return cls.query(getattr(cls, name) == value).get()

  @classmethod
  def get_dbs(cls, query=None, ancestor=None, order=None, limit=None, cursor=None, **kwargs):
    args = parser.parse({
      'cursor': wf.Str(missing=None),
      'limit': wf.Int(missing=None, validate=validate.Range(min=-1)),
      'order': wf.Str(missing=None),
    })
    return util.get_dbs(
      query or cls.query(ancestor=ancestor),
      limit=limit or args['limit'],
      cursor=cursor or args['cursor'],
      order=order or args['order'],
      **kwargs
    )

  FIELDS = {
    'created': fields.DateTime,
    'id': fields.Id,
    'key': fields.Key,
    'modified': fields.DateTime,
    'version': fields.Integer,
  }
