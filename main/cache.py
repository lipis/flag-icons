# coding: utf-8

from google.appengine.api import memcache
import flask

import config
import model


###############################################################################
# Helpers
###############################################################################
def bump_counter(key, time=3600, limit=4):
  client = memcache.Client()
  for _ in range(limit):
    counter = client.gets(key)
    if counter is None:
      client.set(key, 0, time=time)
      counter = 0
    if client.cas(key, counter + 1):
      break


###############################################################################
# Auth Attempts stuff
###############################################################################
def get_auth_attempt_key():
  return 'auth_attempt_%s' % flask.request.remote_addr


def reset_auth_attempt():
  client = memcache.Client()
  client.set(get_auth_attempt_key(), 0, time=3600)


def get_auth_attempt():
  client = memcache.Client()
  return client.get(get_auth_attempt_key()) or 0


def bump_auth_attempt():
  bump_counter(get_auth_attempt_key(), limit=config.SIGNIN_RETRY_LIMIT)


###############################################################################
# Country Stuff
###############################################################################
def get_country_dbs(continent=None):
  key = 'country_dbs_%s' % continent if continent else 'country_dbs'
  country_dbs = memcache.get(key)
  if not country_dbs:
    country_dbs, country_cursor = model.Country.get_dbs(
      limit=-1,
      order='name',
      continent=continent,
    )
    if country_dbs:
      memcache.set(key, country_dbs)
  return country_dbs


def delete_country_dbs():
  memcache.delete('country_dbs')
  for continent in config.CONTINENTS:
    memcache.delete('country_dbs_%s' % continent)
