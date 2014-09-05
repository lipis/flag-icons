# coding: utf-8

from google.appengine.api import memcache


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
