# coding: utf-8

import flask

import cache
import config
import model
import util

from main import app


###############################################################################
# Welcome
###############################################################################
@app.route('/')
def welcome():
  continent = util.param('continent')
  if continent not in model.Country.continent._choices:
    continent = None
  country_dbs = cache.get_country_dbs(continent)
  return flask.render_template(
    'welcome.html',
    html_class='welcome',
    title=continent,
    continent=continent,
    country_dbs=country_dbs,
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
