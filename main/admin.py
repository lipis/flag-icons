# -*- coding: utf-8 -*-

from google.appengine.api import  app_identity
import flask
from flaskext import wtf

import auth
import util
import model
import config

from main import app


class ConfigUpdateForm(wtf.Form):
  analytics_id = wtf.TextField('Analytics ID', filters=[util.strip_filter])
  announcement_html = wtf.TextAreaField('Announcement HTML', filters=[util.strip_filter])
  announcement_type = wtf.SelectField('Announcement Type', choices=[(t, t.title()) for t in model.Config.announcement_type._choices])
  brand_name = wtf.TextField('Brand Name', [wtf.validators.required()], filters=[util.strip_filter])
  facebook_app_id = wtf.TextField('Facebook App ID', filters=[util.strip_filter])
  facebook_app_secret = wtf.TextField('Facebook App Secret', filters=[util.strip_filter])
  feedback_email = wtf.TextField('Feedback Email', [wtf.validators.optional(), wtf.validators.email()], filters=[util.email_filter])
  flask_secret_key = wtf.TextField('Flask Secret Key', [wtf.validators.required()], filters=[util.strip_filter])
  twitter_consumer_key = wtf.TextField('Twitter Consumer Key', filters=[util.strip_filter])
  twitter_consumer_secret = wtf.TextField('Twitter Consumer Secret', filters=[util.strip_filter])


@app.route('/_s/admin/config/', endpoint='admin_config_update_service')
@app.route('/admin/config/', methods=['GET', 'POST'])
@auth.admin_required
def admin_config_update():
  config_db = model.Config.get_master_db()
  form = ConfigUpdateForm(obj=config_db)
  if form.validate_on_submit():
    form.populate_obj(config_db)
    config_db.put()
    reload(config)
    app.config.update(CONFIG_DB=config_db)
    return flask.redirect(flask.url_for('welcome'))

  if flask.request.path.startswith('/_s/'):
    return util.jsonify_model_db(config_db)

  if config.DEBUG:
    instances_url = ''
  else:
    app_id = app_identity.get_application_id()
    version_id = config.CURRENT_VERSION_ID
    instances_url = "https://appengine.google.com/instances?"\
                    "app_id=%s&version_id=%s" % (app_id, version_id)

  return flask.render_template(
      'admin/config_update.html',
      title='Admin Config',
      html_class='admin-config',
      form=form,
      config_db=config_db,
      has_json=True,
      instances_url=instances_url,
    )
