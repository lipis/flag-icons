# coding: utf-8

from __future__ import absolute_import

from google.appengine.ext import ndb

from api import fields
import config
import model
import util


class Config(model.Base, model.ConfigAuth):
  analytics_id = ndb.StringProperty(default='', verbose_name='Tracking ID')
  announcement_html = ndb.TextProperty(default='', verbose_name='Announcement HTML')
  announcement_type = ndb.StringProperty(default='info', choices=['info', 'warning', 'success', 'danger'])
  anonymous_recaptcha = ndb.BooleanProperty(default=False, verbose_name='Use reCAPTCHA in forms for unauthorized users')
  brand_name = ndb.StringProperty(default=config.APPLICATION_ID)
  check_unique_email = ndb.BooleanProperty(default=True, verbose_name='Check for uniqueness of the verified emails')
  email_authentication = ndb.BooleanProperty(default=False, verbose_name='Email authentication for sign in/sign up')
  feedback_email = ndb.StringProperty(default='')
  flask_secret_key = ndb.StringProperty(default=util.uuid())
  notify_on_new_user = ndb.BooleanProperty(default=True, verbose_name='Send an email notification when a user signs up')
  recaptcha_private_key = ndb.StringProperty(default='', verbose_name='Private Key')
  recaptcha_public_key = ndb.StringProperty(default='', verbose_name='Public Key')
  salt = ndb.StringProperty(default=util.uuid())
  verify_email = ndb.BooleanProperty(default=True, verbose_name='Verify user emails')
  letsencrypt_challenge = ndb.StringProperty(default='', verbose_name=u"Let’s Encrypt Challenge")
  letsencrypt_response = ndb.StringProperty(default='', verbose_name=u"Let’s Encrypt Response")

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

  FIELDS = {
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

  FIELDS.update(model.Base.FIELDS)
  FIELDS.update(model.ConfigAuth.FIELDS)
