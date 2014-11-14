# coding: utf-8

from flask.ext import wtf
import flask
import wtforms

import auth
import config
import model
import util

from main import app


###############################################################################
# Admin Stuff
###############################################################################
@app.route('/admin/')
@auth.admin_required
def admin():
  return flask.render_template(
      'admin/admin.html',
      title='Admin',
      html_class='admin',
    )


###############################################################################
# Config Stuff
###############################################################################
class ConfigUpdateForm(wtf.Form):
  analytics_id = wtforms.StringField('Tracking ID', filters=[util.strip_filter])
  announcement_html = wtforms.TextAreaField('Announcement HTML', filters=[util.strip_filter])
  announcement_type = wtforms.SelectField('Announcement Type', choices=[(t, t.title()) for t in model.Config.announcement_type._choices])
  anonymous_recaptcha = wtforms.BooleanField('Use reCAPTCHA in forms for unauthorized users')
  brand_name = wtforms.StringField('Brand Name', [wtforms.validators.required()], filters=[util.strip_filter])
  check_unique_email = wtforms.BooleanField('Check for uniqueness of the verified emails')
  email_authentication = wtforms.BooleanField('Email authentication for sign in/sign up')
  feedback_email = wtforms.StringField('Feedback Email', [wtforms.validators.optional(), wtforms.validators.email()], filters=[util.email_filter])
  flask_secret_key = wtforms.StringField('Flask Secret Key', [wtforms.validators.optional()], filters=[util.strip_filter])
  notify_on_new_user = wtforms.BooleanField('Send an email notification when a user signs up')
  recaptcha_private_key = wtforms.StringField('Private Key', filters=[util.strip_filter])
  recaptcha_public_key = wtforms.StringField('Public Key', filters=[util.strip_filter])
  salt = wtforms.StringField('Salt', [wtforms.validators.optional()], filters=[util.strip_filter])
  verify_email = wtforms.BooleanField('Verify user emails')


@app.route('/_s/admin/config/', endpoint='admin_config_update_service')
@app.route('/admin/config/', methods=['GET', 'POST'])
@auth.admin_required
def admin_config():
  config_db = model.Config.get_master_db()
  form = ConfigUpdateForm(obj=config_db)
  if form.validate_on_submit():
    form.populate_obj(config_db)
    if not config_db.flask_secret_key:
      config_db.flask_secret_key = util.uuid()
    if not config_db.salt:
      config_db.salt = util.uuid()
    config_db.put()
    reload(config)
    app.config.update(CONFIG_DB=config_db)
    return flask.redirect(flask.url_for('admin'))

  if flask.request.path.startswith('/_s/'):
    return util.jsonify_model_db(config_db)

  return flask.render_template(
      'admin/admin_config.html',
      title='App Config',
      html_class='admin-config',
      form=form,
      has_json=True,
    )


###############################################################################
# Auth Stuff
###############################################################################
class AuthUpdateForm(wtf.Form):
  dropbox_app_key = wtforms.StringField('App Key', filters=[util.strip_filter])
  dropbox_app_secret = wtforms.StringField('App Secret', filters=[util.strip_filter])
  facebook_app_id = wtforms.StringField('App ID', filters=[util.strip_filter])
  facebook_app_secret = wtforms.StringField('App Secret', filters=[util.strip_filter])
  github_client_id = wtforms.StringField('Client ID', filters=[util.strip_filter])
  github_client_secret = wtforms.StringField('Client Secret', filters=[util.strip_filter])
  microsoft_client_id = wtforms.StringField('Client ID', filters=[util.strip_filter])
  microsoft_client_secret = wtforms.StringField('Client Secret', filters=[util.strip_filter])
  twitter_consumer_key = wtforms.StringField('Consumer Key', filters=[util.strip_filter])
  twitter_consumer_secret = wtforms.StringField('Consumer Secret', filters=[util.strip_filter])


@app.route('/_s/admin/auth/', endpoint='admin_auth_service')
@app.route('/admin/auth/', methods=['GET', 'POST'])
@auth.admin_required
def admin_auth():
  config_db = model.Config.get_master_db()
  form = AuthUpdateForm(obj=config_db)
  if form.validate_on_submit():
    form.populate_obj(config_db)
    config_db.put()
    reload(config)
    app.config.update(CONFIG_DB=config_db)
    return flask.redirect(flask.url_for('admin'))

  if flask.request.path.startswith('/_s/'):
    return util.jsonify_model_db(config_db)

  return flask.render_template(
      'admin/admin_auth.html',
      title='Auth Config',
      html_class='admin-auth',
      form=form,
      has_json=True,
    )
