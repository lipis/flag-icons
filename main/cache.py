# coding: utf-8

from google.appengine.api import memcache
import flask

import config


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
