# coding: utf-8

from urlparse import urlparse
from uuid import uuid4
import hashlib
import re
import unicodedata
import urllib

from google.appengine.datastore.datastore_query import Cursor
from google.appengine.ext import ndb
from webargs import fields as wf
from webargs.flaskparser import parser
import flask

import config


###############################################################################
# Request Parameters
###############################################################################
def param(name, cast=None):
  def switch(case):
    return {
      int: wf.Int(missing=None),
      float: wf.Float(missing=None),
      bool: wf.Bool(missing=None),
      list: wf.DelimitedList(wf.Str(), delimiter=',', missing=[]),
    }.get(case)
  if cast is None or cast is ndb.Key:
    cast_ = wf.Str(missing=None)
  else:
    cast_ = switch(cast) or cast
  args = parser.parse({name: cast_})
  value = args[name]
  return ndb.Key(urlsafe=value) if cast is ndb.Key and value else value


def is_trusted_url(next_url):
  if not next_url:
    return ''
  next_url_host = urlparse(next_url).hostname
  if config.TRUSTED_HOSTS and next_url_host not in config.TRUSTED_HOSTS:
    return flask.url_for('welcome')
  if not next_url.startswith(flask.request.host_url):
    return flask.url_for('welcome')
  return next_url


def get_next_url(next_url=''):
  args = parser.parse({
    'next': wf.Str(missing=None), 'next_url': wf.Str(missing=None)
  })
  next_url = next_url or args['next'] or args['next_url']
  if next_url:
    do_not_redirect_urls = [flask.url_for(u) for u in [
      'signin', 'signup', 'user_forgot', 'user_reset',
    ]]
    if any(url in next_url for url in do_not_redirect_urls):
      return flask.url_for('welcome')
    return is_trusted_url(next_url)
  return is_trusted_url(flask.request.referrer)


###############################################################################
# Model manipulations
###############################################################################
def get_dbs(
        query, order=None, limit=None, cursor=None, prev_cursor=False,
        keys_only=None, **filters
):
  model_class = ndb.Model._kind_map[query.kind]
  query_prev = query
  if order:
    for o in order.split(','):
      if o.startswith('-'):
        query = query.order(-model_class._properties[o[1:]])
        if prev_cursor:
          query_prev = query_prev.order(model_class._properties[o[1:]])
      else:
        query = query.order(model_class._properties[o])
        if prev_cursor:
          query_prev = query_prev.order(-model_class._properties[o])

  for prop, value in filters.iteritems():
    if value is None:
      continue
    for val in value if isinstance(value, list) else [value]:
      query = query.filter(model_class._properties[prop] == val)
      if prev_cursor:
        query_prev = query_prev.filter(model_class._properties[prop] == val)

  limit = limit or config.DEFAULT_DB_LIMIT
  if limit == -1:
    return list(query.fetch(keys_only=keys_only)), {'next': None, 'prev': None}

  cursor = Cursor.from_websafe_string(cursor) if cursor else None
  model_dbs, next_cursor, more = query.fetch_page(
    limit, start_cursor=cursor, keys_only=keys_only,
  )
  next_cursor = next_cursor.to_websafe_string() if more else None
  if not prev_cursor:
    return list(model_dbs), {'next': next_cursor, 'prev': None}
  model_dbs_prev, prev_cursor, prev_more = query_prev.fetch_page(
    limit, start_cursor=cursor.reversed() if cursor else None, keys_only=True
  )
  prev_cursor = prev_cursor.reversed().to_websafe_string() \
      if prev_cursor and cursor else None
  return list(model_dbs), {'next': next_cursor, 'prev': prev_cursor}


def get_keys(*arg, **kwargs):
  return get_dbs(*arg, keys_only=True, **kwargs)


###############################################################################
# JSON Response Helpers
###############################################################################
def jsonpify(*args, **kwargs):
  params = parser.parse({'callback': wf.Str(missing=None)})
  if params['callback']:
    content = '%s(%s)' % (
      params['callback'], flask.jsonify(*args, **kwargs).data,
    )
    mimetype = 'application/javascript'
    return flask.current_app.response_class(content, mimetype=mimetype)
  return flask.jsonify(*args, **kwargs)


###############################################################################
# Helpers
###############################################################################
def is_iterable(value):
  return isinstance(value, (tuple, list))


def check_form_fields(*fields):
  fields_data = []
  for field in fields:
    if is_iterable(field):
      fields_data.extend([field.data for field in field])
    else:
      fields_data.append(field.data)
  return all(fields_data)


def generate_next_url(next_cursor, base_url=None, cursor_name='cursor'):
  if isinstance(next_cursor, dict):
    next_cursor = next_cursor.get('next')
  if not next_cursor:
    return None
  base_url = base_url or flask.request.base_url
  args = flask.request.args.to_dict()
  args[cursor_name] = next_cursor
  return '%s?%s' % (base_url, urllib.urlencode(args))


def uuid():
  return uuid4().hex


_slugify_strip_re = re.compile(r'[^\w\s-]')
_slugify_hyphenate_re = re.compile(r'[-\s]+')


def slugify(text):
  if not isinstance(text, unicode):
    text = unicode(text)
  text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')
  text = unicode(_slugify_strip_re.sub('', text).strip().lower())
  return _slugify_hyphenate_re.sub('-', text)


_username_re = re.compile(r'^[a-z0-9]+(?:[\.][a-z0-9]+)*$')


def is_valid_username(username):
  return bool(_username_re.match(username))


def create_name_from_email(email):
  return re.sub(r'_+|-+|\.+|\++', ' ', email.split('@')[0]).title()


def password_hash(user_db, password):
  m = hashlib.sha256()
  m.update(user_db.key.urlsafe())
  m.update(user_db.created.isoformat())
  m.update(m.hexdigest())
  m.update(password.encode('utf-8'))
  m.update(config.CONFIG_DB.salt)
  return m.hexdigest()


def update_query_argument(name, value=None, ignore='cursor', is_list=False):
  ignore = ignore.split(',') if isinstance(ignore, str) else ignore or []
  arguments = {}
  for key, val in flask.request.args.items():
    if key not in ignore and (is_list and value is not None or key != name):
      arguments[key] = val
  if value is not None:
    if is_list:
      values = []
      if name in arguments:
        values = arguments[name].split(',')
        del arguments[name]
      if value in values:
        values.remove(value)
      else:
        values.append(value)
      if values:
        arguments[name] = ','.join(values)
    else:
      arguments[name] = value
  query = '&'.join('%s=%s' % item for item in sorted(arguments.items()))
  return '%s%s' % (flask.request.path, '?%s' % query if query else '')


def parse_tags(tags, separator=None):
  if not is_iterable(tags):
    tags = unicode(tags.strip()).split(separator or config.TAG_SEPARATOR)
  return filter(None, sorted(list(set(tags))))


###############################################################################
# Lambdas
###############################################################################
strip_filter = lambda x: x.strip() if x else ''
email_filter = lambda x: x.lower().strip() if x else ''
sort_filter = lambda x: sorted(x) if x else []
