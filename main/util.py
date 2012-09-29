from google.appengine.datastore.datastore_query import Cursor
from google.appengine.ext import ndb
import flask

from uuid import uuid4
from datetime import datetime
import urllib

import config


################################################################################
# Request Parameters
################################################################################
def param(name, cast=None):
  '''Returs query parameter by its name, and optionaly casts it to given type.
  Always returns None if the parameter is missing
  '''
  res = None
  if flask.request.json:
    return flask.request.json.get(name, None)

  if res is None:
    res = flask.request.args.get(name, None)
  if res is None and flask.request.form:
    res = flask.request.form.get(name, None)

  if cast and res:
    if cast == bool:
      return res == 'true'
    return cast(res)
  return res


def get_next_url():
  next = param('next')
  if next:
    return next
  referrer = flask.request.referrer
  if referrer and referrer.startswith(flask.request.host_url):
    return referrer
  return flask.url_for('welcome')


################################################################################
# Model manipulations
################################################################################
def retrieve_dbs(model_class, query, order=None, limit=None, cursor=None,
                 **filters):
  ''' Retrieves entities from datastore, by applying cursor pagindation
  and equality filters. Returns dbs and more cursor value
  '''
  limit = limit or config.DEFAULT_DB_LIMIT
  if cursor:
    cursor = Cursor.from_websafe_string(cursor)

  #apply order if any
  if order:
    for o in order.split(','):
      if o.startswith('-'):
        query = query.order(-model_class._properties[o[1:]])
      else:
        query = query.order(model_class._properties[o])

  for prop in filters:
    if filters.get(prop, None) is None:
      continue
    if type(filters[prop]) == list:
      for value in filters[prop]:
        query = query.filter(model_class._properties[prop] == value)
    else:
      query = query.filter(model_class._properties[prop] == filters[prop])

  model_dbs, more_cursor, more = query.fetch_page(limit, start_cursor=cursor)
  if not more:
    more_cursor = None
  else:
    more_cursor = more_cursor.to_websafe_string()
  return list(model_dbs), more_cursor


################################################################################
# Json Response Helpers
################################################################################
def jsonify_model_dbs(model_dbs, more_cursor=None):
  '''Return a response of a list of dbs as JSON service result
  '''
  now = datetime.utcnow()
  result_objects = []
  for model_db in model_dbs:
    result_objects.append(model_db_to_object(model_db, now))

  response_object = {
      'status': 'success',
      'count': len(result_objects),
      'now': format_datetime_utc(now),
      'result': result_objects,
    }
  if more_cursor:
    response_object['more_cursor'] = more_cursor
    response_object['more_url'] = generate_more_url(more_cursor)
  response = flask.jsonify(response_object)
  return response


def jsonify_model_db(model_db):
  '''Return respons of a db as JSON service result
  '''
  now = datetime.utcnow()
  result_object = model_db_to_object(model_db, now)
  response = flask.jsonify({
      'status': 'success',
      'now': format_datetime_utc(now),
      'result': result_object,
    })
  return response


def model_db_to_object(model_db, now=None):
  if not now:
    now = datetime.utcnow()
  model_db_object = {}
  for prop in model_db._PROPERTIES:
    if prop == 'id':
      value = getattr(model_db, 'key', None).id()
    else:
      value = getattr(model_db, prop, None)

    if type(value) == datetime:
      model_db_object[prop] = format_datetime_utc(value)
    elif type(value) == ndb.Key:
      model_db_object[prop] = value.urlsafe()
    elif type(value) == ndb.GeoPt:
      model_db_object[prop] = '%s,%s' % (value.lat, value.lon)
    elif value is not None:
      model_db_object[prop] = value
  return model_db_object


################################################################################
# Helpers
################################################################################
def generate_more_url(more_cursor, base_url=None):
  '''Substitutes or alters the current request url with a new cursor parameter
  for next page of results
  '''
  if not more_cursor:
    return None
  base_url = base_url or flask.request.base_url
  args = flask.request.args.to_dict()
  args['cursor'] = more_cursor
  return '%s?%s' % (base_url, urllib.urlencode(args))


def uuid():
  ''' Generates universal unique identifier
  '''
  return str(uuid4()).replace('-', '')


################################################################################
# In Time
################################################################################
def format_datetime_utc(datetime):
  return datetime.strftime("%Y-%m-%d %H:%M:%S UTC")


SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR
MONTH = 30 * DAY


def format_datetime_ago(timestamp):
  delta = datetime.utcnow() - timestamp
  seconds = delta.seconds + delta.days * DAY
  minutes = 1.0 * seconds / MINUTE
  hours = 1.0 * seconds / HOUR
  days = 1.0 * seconds / DAY
  months = 1.0 * seconds / MONTH
  years = days / 365

  if seconds < 0:
    return 'not yet'
  if seconds < 1 * MINUTE:
    return '%d seconds ago' % seconds
  if seconds < 2 * MINUTE:
    return 'a minute ago'
  if seconds < 45 * MINUTE:
    return '%0.0f minutes ago' % minutes
  if seconds < 90 * MINUTE:
    return 'an hour ago'
  if seconds < 24 * HOUR:
    return '%0.0f hours ago' % hours
  if seconds < 48 * HOUR:
    return 'yesterday'
  if seconds < 30 * DAY:
    return '%0.0f days ago' % days
  if seconds < 12 * MONTH:
    if months < 1.5:
      return 'one month ago'
    else:
      return '%0.0f months ago' % months
  else:
    if years <= 1:
      return 'one year ago'
    else:
      return '%d years ago' % years
