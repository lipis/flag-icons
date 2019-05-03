# coding: utf-8

from google.appengine.ext import ndb
import flask
import wtforms

import i18n
import auth
import cache
import config
import model
import util

from main import app


###############################################################################
# List
###############################################################################
@app.route('/country/')
def country_list():
  country_dbs, country_cursor = model.Country.get_dbs()
  return flask.render_template(
    'country/country_list.html',
    html_class='country-list',
    title='Country List',
    country_dbs=country_dbs,
    next_url=util.generate_next_url(country_cursor),
    api_url=flask.url_for('api.country.list'),
  )


###############################################################################
# View
###############################################################################
@app.route('/country/<int:country_id>/')
def country_view(country_id):
  country_db = model.Country.get_by_id(country_id)
  if not country_db:
    flask.abort(404)

  return flask.render_template(
    'country/country_view.html',
    html_class='country-view',
    title=country_db.name,
    country_db=country_db,
    api_url=flask.url_for('api.country', country_key=country_db.key.urlsafe() if country_db.key else ''),
  )


###############################################################################
# Admin List
###############################################################################
@app.route('/admin/country/')
@auth.admin_required
def admin_country_list():
  country_dbs, country_cursor = model.Country.get_dbs(
    order=util.param('order') or '-modified',
  )
  return flask.render_template(
    'country/admin_country_list.html',
    html_class='admin-country-list',
    title='Country List',
    country_dbs=country_dbs,
    next_url=util.generate_next_url(country_cursor),
    api_url=flask.url_for('api.admin.country.list'),
  )


###############################################################################
# Admin Update
###############################################################################
class CountryUpdateAdminForm(i18n.Form):
  name = wtforms.StringField(
    model.Country.name._verbose_name,
    [wtforms.validators.required()],
    filters=[util.strip_filter],
  )
  capital = wtforms.StringField(
    model.Country.capital._verbose_name,
    [wtforms.validators.required()],
    filters=[util.strip_filter],
  )
  alpha_2 = wtforms.StringField(
    model.Country.alpha_2._verbose_name,
    [wtforms.validators.required()],
    filters=[util.upper_filter],
  )
  alpha_3 = wtforms.StringField(
    model.Country.alpha_3._verbose_name,
    [wtforms.validators.required()],
    filters=[util.upper_filter],
  )
  continent = wtforms.SelectField(
    model.Country.continent._verbose_name,
    [wtforms.validators.required()],
    choices=[(c, c) for c in sorted(model.Country.continent._choices)],
  )
  iso = wtforms.BooleanField(
    model.Country.iso._verbose_name,
    [wtforms.validators.optional()],
  )


@app.route('/admin/country/create/', methods=['GET', 'POST'])
@app.route('/admin/country/<int:country_id>/update/', methods=['GET', 'POST'])
@auth.admin_required
def admin_country_update(country_id=0):
  if country_id:
    country_db = model.Country.get_by_id(country_id)
  else:
    country_db = model.Country()

  if not country_db:
    flask.abort(404)

  form = CountryUpdateAdminForm(obj=country_db)

  if form.validate_on_submit():
    form.populate_obj(country_db)
    country_db.put()
    cache.delete_country_dbs()
    return flask.redirect(flask.url_for('country_list', order='-modified'))

  return flask.render_template(
    'country/admin_country_update.html',
    title='%s' % country_db.name if country_id else 'New Country',
    html_class='admin-country-update',
    form=form,
    country_db=country_db,
    back_url_for='admin_country_list',
    api_url=flask.url_for('api.admin.country', country_key=country_db.key.urlsafe() if country_db.key else ''),
  )
