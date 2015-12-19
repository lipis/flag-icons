# coding: utf-8

import flask

import config

from main import app


@app.route('/.well-known/acme-challenge/<challenge>')
def letsencrypt(challenge):
  response = flask.make_response('oups', 404)
  if challenge == config.CONFIG_DB.letsencrypt_challenge:
    response = flask.make_response(config.CONFIG_DB.letsencrypt_response)
  response.headers['Content-Type'] = 'text/plain'
  return response
