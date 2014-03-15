# -*- coding: utf-8 -*-

import flask
from google.appengine.api import mail
from google.appengine.ext import deferred

import config


def send_mail_notification(subject, body, **kwargs):
  if not config.CONFIG_DB.feedback_email:
    return
  brand_name = config.CONFIG_DB.brand_name
  sender = '%s <%s>' % (brand_name, config.CONFIG_DB.feedback_email)
  subject = '[%s] %s' % (brand_name, subject)
  deferred.defer(mail.send_mail, sender, sender, subject, body, **kwargs)
