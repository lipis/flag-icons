# coding: utf-8

from __future__ import absolute_import

from flask.ext.babel import lazy_gettext as _
from google.appengine.ext import ndb

from api import fields
import model
import util


class Country(model.Base):
  name = ndb.StringProperty(required=True, verbose_name=_(u'Name'))
  capital = ndb.StringProperty(required=True, verbose_name=_(u'Capital'))
  alpha_2 = ndb.StringProperty(required=True, verbose_name=_(u'Alpha-2 Code'))
  alpha_3 = ndb.StringProperty(required=True, verbose_name=_(u'Alpha 3 Code'))
  continent = ndb.StringProperty(required=True, choices=['Africa', 'Asia', 'Australia', 'Europe', 'North America', 'South America'], verbose_name=_(u'Continent'))
  iso = ndb.BooleanProperty(default=True, verbose_name=_(u'ISO'))

  @classmethod
  def get_dbs(cls, order=None, **kwargs):
    return super(Country, cls).get_dbs(
      order=order or util.param('order') or 'name',
      **kwargs
    )

  FIELDS = {
    'name': fields.String,
    'capital': fields.String,
    'alpha_2': fields.String,
    'alpha_3': fields.String,
    'continent': fields.String,
    'iso': fields.Boolean,
  }

  FIELDS.update(model.Base.FIELDS)
