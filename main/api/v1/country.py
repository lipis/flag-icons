# coding: utf-8

from __future__ import absolute_import

from google.appengine.ext import ndb
import flask_restful
import flask

from api import helpers
import auth
import cache
import model
import util

from main import api_v1


@api_v1.resource('/country/', endpoint='api.country.list')
class CountryListAPI(flask_restful.Resource):
  def get(self):
    country_dbs = cache.get_country_dbs()
    return helpers.make_response(country_dbs, model.Country.FIELDS)


@api_v1.resource('/country/<string:country_key>/', endpoint='api.country')
class CountryAPI(flask_restful.Resource):
  def get(self, country_key):
    country_db = ndb.Key(urlsafe=country_key).get()
    if not country_db:
      helpers.make_not_found_exception('Country %s not found' % country_key)
    return helpers.make_response(country_db, model.Country.FIELDS)


###############################################################################
# Admin
###############################################################################
@api_v1.resource('/admin/country/', endpoint='api.admin.country.list')
class AdminCountryListAPI(flask_restful.Resource):
  @auth.admin_required
  def get(self):
    country_keys = util.param('country_keys', list)
    if country_keys:
      country_db_keys = [ndb.Key(urlsafe=k) for k in country_keys]
      country_dbs = ndb.get_multi(country_db_keys)
      return helpers.make_response(country_dbs, model.country.FIELDS)

    country_dbs, country_cursor = model.Country.get_dbs()
    return helpers.make_response(country_dbs, model.Country.FIELDS, country_cursor)


@api_v1.resource('/admin/country/<string:country_key>/', endpoint='api.admin.country')
class AdminCountryAPI(flask_restful.Resource):
  @auth.admin_required
  def get(self, country_key):
    country_db = ndb.Key(urlsafe=country_key).get()
    if not country_db:
      helpers.make_not_found_exception('Country %s not found' % country_key)
    return helpers.make_response(country_db, model.Country.FIELDS)
