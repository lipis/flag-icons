# coding: utf-8

import logging

import flask
import werkzeug

from api import helpers
import config

from main import app


@app.errorhandler(400)  # Bad Request
@app.errorhandler(401)  # Unauthorized
@app.errorhandler(403)  # Forbidden
@app.errorhandler(404)  # Not Found
@app.errorhandler(405)  # Method Not Allowed
@app.errorhandler(410)  # Gone
@app.errorhandler(418)  # I'm a Teapot
@app.errorhandler(422)  # Unprocessable Entity
@app.errorhandler(500)  # Internal Server Error
def error_handler(e):
  try:
    e.code
  except AttributeError:
    e.code = 500
    e.name = 'Internal Server Error'

  logging.error('%d - %s: %s', e.code, e.name, flask.request.url)
  if e.code != 404:
    logging.exception(e)

  if flask.request.path.startswith('/api/'):
    return helpers.handle_error(e)

  return flask.render_template(
    'error.html',
    title='Error %d (%s)!!1' % (e.code, e.name),
    html_class='error-page',
    error=e,
  ), e.code


if config.PRODUCTION:
  @app.errorhandler(Exception)
  def production_error_handler(e):
    if isinstance(e, werkzeug.exceptions.HTTPException) and e.code in (301, 302):
      return e
    return error_handler(e)
