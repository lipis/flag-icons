import flask
from flaskext import wtf

import auth
import util
import model
import config

from main import app


class ConfigUpdateForm(wtf.Form):
  brand_name = wtf.TextField(
      'Brand Name', [wtf.validators.required()]
    )
  analytics_id = wtf.TextField(
      'Analytics ID', [wtf.validators.optional()]
    )
  facebook_app_id = wtf.TextField(
      'Facebook ID', [wtf.validators.optional()]
    )
  facebook_app_secret = wtf.TextField(
      'Facebook Secret', [wtf.validators.optional()]
    )
  feedback_email = wtf.TextField('Feedback Email', [
        wtf.validators.optional(),
        wtf.validators.email('That does not look like an email'),
      ])
  twitter_consumer_key = wtf.TextField(
      'Twitter Key', [wtf.validators.optional()]
    )
  twitter_consumer_secret = wtf.TextField(
      'Twitter Secret', [wtf.validators.optional()]
    )
  flask_secret_key = wtf.TextField(
      'Flask Secret Key', [wtf.validators.required()]
    )


@app.route('/_s/admin/config/', endpoint='admin_config_update_service')
@app.route(
    '/admin/config/', methods=['GET', 'POST'], endpoint='admin_config_update',
  )
@auth.admin_required
def admin_config_update():
  form = ConfigUpdateForm()

  config_db = model.Config.get_master_db()
  if form.validate_on_submit():
    config_db.analytics_id = form.analytics_id.data
    config_db.brand_name = form.brand_name.data
    config_db.facebook_app_id = form.facebook_app_id.data
    config_db.facebook_app_secret = form.facebook_app_secret.data
    config_db.feedback_email = form.feedback_email.data
    config_db.flask_secret_key = form.flask_secret_key.data
    config_db.twitter_consumer_key = form.twitter_consumer_key.data
    config_db.twitter_consumer_secret = form.twitter_consumer_secret.data
    config_db.put()
    reload(config)
    app.config.update(CONFIG_DB=config_db)
    flask.flash('Your config settings have been saved', category='success')
    return flask.redirect(flask.url_for('welcome'))
  if not form.errors:
    form.analytics_id.data = config_db.analytics_id
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
