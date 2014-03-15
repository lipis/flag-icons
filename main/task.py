# -*- coding: utf-8 -*-

import flask
from google.appengine.api import mail
from google.appengine.ext import deferred

import config


###############################################################################
# Helpers
###############################################################################
def send_mail_notification(subject, body, **kwargs):
  if not config.CONFIG_DB.feedback_email:
    return
  brand_name = config.CONFIG_DB.brand_name
  sender = '%s <%s>' % (brand_name, config.CONFIG_DB.feedback_email)
  subject = '[%s] %s' % (brand_name, subject)
  deferred.defer(mail.send_mail, sender, sender, subject, body, **kwargs)


###############################################################################
# User related
###############################################################################
def new_user_notification(user_db):
  if not config.CONFIG_DB.notify_on_new_user:
    return
  update_url = '%s%s' % (
      flask.request.host_url[:-1],
      flask.url_for('user_update', user_id=user_db.key.id()),
    )
  body = 'name: %s\nusername: %s\nemail: %s\n%s\n%s' % (
      user_db.name,
      user_db.username,
      user_db.email,
      ''.join([': '.join(('%s\n' % a).split('_')) for a in user_db.auth_ids]),
      update_url,
    )
  send_mail_notification('New user: %s' % user_db.name, body)
