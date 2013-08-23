# -*- coding: utf-8 -*-

import flask
from flaskext import wtf

import auth
import util
import model
import config

from main import app


class ConfigUpdateForm(wtf.Form):
  analytics_id = wtf.TextField('Analytics ID')
  announcement_html = wtf.TextAreaField('Announcement HTML')
  announcement_type = wtf.SelectField('Announcement Type', choices=[
      (s, s.title()) for s in model.Config.announcement_type._choices
    ])
  brand_name = wtf.TextField('Brand Name', [wtf.validators.required()])
  facebook_app_id = wtf.TextField('Facebook App ID')
  facebook_app_secret = wtf.TextField('Facebook App Secret')
  feedback_email = wtf.TextField('Feedback Email', [
      wtf.optional(),
      wtf.validators.email('That does not look like an email')
    ])
  flask_secret_key = wtf.TextField('Flask Secret Key', [wtf.validators.required()])
  twitter_consumer_key = wtf.TextField('Twitter Consumer Key')
  twitter_consumer_secret = wtf.TextField('Twitter Consumer Secret')


@app.route('/_s/admin/config/', endpoint='admin_config_update_service')
@app.route('/admin/config/', methods=['GET', 'POST'])
@auth.admin_required
def admin_config_update():
  form = ConfigUpdateForm()

  config_db = model.Config.get_master_db()
  if form.validate_on_submit():
    config_db.analytics_id = form.analytics_id.data.strip()
    config_db.announcement_html = form.announcement_html.data.strip()
    config_db.announcement_type = form.announcement_type.data.strip()
    config_db.brand_name = form.brand_name.data.strip()
    config_db.facebook_app_id = form.facebook_app_id.data.strip()
    config_db.facebook_app_secret = form.facebook_app_secret.data.strip()
    config_db.feedback_email = form.feedback_email.data.strip()
    config_db.flask_secret_key = form.flask_secret_key.data.strip()
    config_db.twitter_consumer_key = form.twitter_consumer_key.data.strip()
    config_db.twitter_consumer_secret = form.twitter_consumer_secret.data.strip()
    config_db.put()
    reload(config)
    app.config.update(CONFIG_DB=config_db)
    return flask.redirect(flask.url_for('welcome'))
  if not form.errors:
    form.analytics_id.data = config_db.analytics_id
    form.announcement_html.data = config_db.announcement_html
    form.announcement_type.data = config_db.announcement_type
    form.brand_name.data = config_db.brand_name
    form.facebook_app_id.data = config_db.facebook_app_id
    form.facebook_app_secret.data = config_db.facebook_app_secret
    form.feedback_email.data = config_db.feedback_email
    form.flask_secret_key.data = config_db.flask_secret_key
    form.twitter_consumer_key.data = config_db.twitter_consumer_key
    form.twitter_consumer_secret.data = config_db.twitter_consumer_secret

  if flask.request.path.startswith('/_s/'):
    return util.jsonify_model_db(config_db)

  return flask.render_template(
      'admin/config_update.html',
      title='Admin Config',
      html_class='admin-config',
      form=form,
      config_db=config_db,
    )
