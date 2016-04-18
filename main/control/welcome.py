# coding: utf-8

import flask

import config
import model
import util

from main import app


###############################################################################
# Welcome
###############################################################################
@app.route('/')
def welcome():
  country_dbs, country_cursor = model.Country.get_dbs(limit=-1)
  return flask.render_template(
    'welcome.html',
    html_class='welcome',
    country_dbs=country_dbs,
    next_url=util.generate_next_url(country_cursor),
    api_url=flask.url_for('api.country.list'),
  )


###############################################################################
# Sitemap stuff
###############################################################################
@app.route('/sitemap.xml')
def sitemap():
  response = flask.make_response(flask.render_template(
    'sitemap.xml',
    lastmod=config.CURRENT_VERSION_DATE.strftime('%Y-%m-%d'),
  ))
  response.headers['Content-Type'] = 'application/xml'
  return response


###############################################################################
# Warmup request
###############################################################################
@app.route('/_ah/warmup')
def warmup():
  # TODO: put your warmup code here
  return 'success'
