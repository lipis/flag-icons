# coding: utf-8

from __future__ import absolute_import

from flask.ext.restful import fields
from google.appengine.ext import ndb

import config
import model
import util


class Config(model.Base, model.ConfigAuth):
  analytics_id = ndb.StringProperty(default='')
  announcement_html = ndb.TextProperty(default='')
  announcement_type = ndb.StringProperty(default='info', choices=[
      'info', 'warning', 'success', 'danger',
    ])
  anonymous_recaptcha = ndb.BooleanProperty(default=False)
  brand_name = ndb.StringProperty(default=config.APPLICATION_ID)
  check_unique_email = ndb.BooleanProperty(default=True)
  email_authentication = ndb.BooleanProperty(default=False)
  feedback_email = ndb.StringProperty(default='')
  flask_secret_key = ndb.StringProperty(default=util.uuid())
  notify_on_new_user = ndb.BooleanProperty(default=True)
  recaptcha_private_key = ndb.StringProperty(default='')
  recaptcha_public_key = ndb.StringProperty(default='')
  salt = ndb.StringProperty(default=util.uuid())
  verify_email = ndb.BooleanProperty(default=True)

  @property
  def has_anonymous_recaptcha(self):
    return bool(self.anonymous_recaptcha and self.has_recaptcha)

  @property
  def has_email_authentication(self):
    return bool(self.email_authentication and self.feedback_email and self.verify_email)

  @property
  def has_recaptcha(self):
    return bool(self.recaptcha_private_key and self.recaptcha_public_key)

  @classmethod
  def get_master_db(cls):
    return cls.get_or_insert('master')


CONFIG_FIELDS = {
    'analytics_id': fields.String,
    'announcement_html': fields.String,
    'announcement_type': fields.String,
    'anonymous_recaptcha': fields.Boolean,
    'brand_name': fields.String,
    'check_unique_email': fields.Boolean,
    'email_authentication': fields.Boolean,
    'feedback_email': fields.String,
    'flask_secret_key': fields.String,
    'notify_on_new_user': fields.Boolean,
    'recaptcha_private_key': fields.String,
    'recaptcha_public_key': fields.String,
    'salt': fields.String,
    'verify_email': fields.Boolean,
  }

CONFIG_FIELDS.update(model.BASE_FIELDS)
