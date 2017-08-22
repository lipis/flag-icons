# coding: utf-8

from datetime import datetime
import logging

from werkzeug import exceptions
import flask
import flask_restful

import util


class Api(flask_restful.Api):
  def unauthorized(self, response):
    flask.abort(401)

  def handle_error(self, e):
    return handle_error(e)


def handle_error(e):
  logging.exception(e)
  try:
    e.code
  except AttributeError:
    e.code = 500
    e.name = e.description = 'Internal Server Error'
  return util.jsonpify({
    'status': 'error',
    'error_code': e.code,
    'error_name': util.slugify(e.name),
    'error_message': e.name,
    'error_class': e.__class__.__name__,
    'description': e.description,
  }), e.code


def make_response(data, marshal_table, cursors=None):
  if util.is_iterable(data):
    response = {
      'status': 'success',
      'count': len(data),
      'now': datetime.utcnow().isoformat(),
      'result': [flask_restful.marshal(d, marshal_table) for d in data],
    }
    if cursors:
      if isinstance(cursors, dict):
        if cursors.get('next'):
          response['next_cursor'] = cursors['next']
          response['next_url'] = util.generate_next_url(cursors['next'])
        if cursors.get('prev'):
          response['prev_cursor'] = cursors['prev']
          response['prev_url'] = util.generate_next_url(cursors['prev'])
      else:
        response['next_cursor'] = cursors
        response['next_url'] = util.generate_next_url(cursors)
    return util.jsonpify(response)
  return util.jsonpify({
    'status': 'success',
    'now': datetime.utcnow().isoformat(),
    'result': flask_restful.marshal(data, marshal_table),
  })


def make_not_found_exception(description):
  exception = exceptions.NotFound()
  exception.description = description
  raise exception
