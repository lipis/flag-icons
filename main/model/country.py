# coding: utf-8

from __future__ import absolute_import

from flask_babel import lazy_gettext as _
from google.appengine.ext import ndb

from api import fields

import config
import model
import util

CONTINENTS = [
  'Africa',
  'Antarctica',
  'Asia',
  'Europe',
  'North America',
  'Oceania',
  'South America',
]

class Country(model.Base):
  name = ndb.StringProperty(required=True, verbose_name=_(u'Name'))
  capital = ndb.StringProperty(required=True, verbose_name=_(u'Capital'))
  alpha_2 = ndb.StringProperty(required=True, verbose_name=_(u'Alpha-2 Code'))
  alpha_3 = ndb.StringProperty(required=True, verbose_name=_(u'Alpha 3 Code'))
  continent = ndb.StringProperty(required=False, choices=CONTINENTS, verbose_name=_(u'Continent'))
  iso = ndb.BooleanProperty(default=True, verbose_name=_(u'ISO'))

  @ndb.ComputedProperty
  def flag_4x3(self):
    return 'https://lipis.github.io/flag-icon-css/flags/4x3/%s.svg' % self.alpha_2.lower()

  @ndb.ComputedProperty
  def flag_1x1(self):
    return 'https://lipis.github.io/flag-icon-css/flags/1x1/%s.svg' % self.alpha_2.lower()

  @classmethod
  def get_dbs(cls, order=None, **kwargs):
    return super(Country, cls).get_dbs(
      order=order or util.param('order') or 'name',
      **kwargs
    )

  FIELDS = {
    'alpha_2': fields.String,
    'alpha_3': fields.String,
    'capital': fields.String,
    'continent': fields.String,
    'flag_1x1': fields.String,
    'flag_4x3': fields.String,
    'iso': fields.Boolean,
    'name': fields.String,
  }

  FIELDS.update(model.Base.FIELDS)
