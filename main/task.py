# coding: utf-8

import logging

import flask
from google.appengine.api import mail
from google.appengine.ext import deferred

import config
import util


###############################################################################
# Helpers
###############################################################################
def send_mail_notification(subject, body, to=None, **kwargs):
  if not config.CONFIG_DB.feedback_email:
    return
  brand_name = config.CONFIG_DB.brand_name
  sender = '%s <%s>' % (brand_name, config.CONFIG_DB.feedback_email)
  subject = '[%s] %s' % (brand_name, subject)
  if config.DEVELOPMENT:
    logging.info(
      '\n'
      '######### Deferring to send this email: #############################'
      '\nFrom: %s\nTo: %s\nSubject: %s\n\n%s\n'
      '#####################################################################',
      sender, to or sender, subject, body
    )
  deferred.defer(mail.send_mail, sender, to or sender, subject, body, **kwargs)


###############################################################################
# Admin Notifications
###############################################################################
def new_user_notification(user_db):
  if not config.CONFIG_DB.notify_on_new_user:
    return
  body = 'name: %s\nusername: %s\nemail: %s\n%s\n%s' % (
    user_db.name,
    user_db.username,
    user_db.email,
    ''.join([': '.join(('%s\n' % a).split('_')) for a in user_db.auth_ids]),
    flask.url_for('user_update', user_id=user_db.key.id(), _external=True),
  )
  send_mail_notification('New user: %s' % user_db.name, body)


###############################################################################
# User Related
###############################################################################
def verify_email_notification(user_db):
  if not (config.CONFIG_DB.verify_email and user_db.email) or user_db.verified:
    return
  user_db.token = util.uuid()
  user_db.put()

  to = '%s <%s>' % (user_db.name, user_db.email)
  body = '''Hello %(name)s,

it seems someone (hopefully you) tried to verify your email with %(brand)s.

In case it was you, please verify it by following this link:

%(link)s

If it wasn't you, we apologize. You can either ignore this email or reply to it
so we can take a look.

Best regards,
%(brand)s
''' % {
    'name': user_db.name,
    'link': flask.url_for('user_verify', token=user_db.token, _external=True),
    'brand': config.CONFIG_DB.brand_name,
  }

  flask.flash(
    'A verification link has been sent to your email address.',
    category='success',
  )
  send_mail_notification('Verify your email.', body, to)


def reset_password_notification(user_db):
  if not user_db.email:
    return
  user_db.token = util.uuid()
  user_db.put()

  to = '%s <%s>' % (user_db.name, user_db.email)
  body = '''Hello %(name)s,

it seems someone (hopefully you) tried to reset your password with %(brand)s.

In case it was you, please reset it by following this link:

%(link)s

If it wasn't you, we apologize. You can either ignore this email or reply to it
so we can take a look.

Best regards,
%(brand)s
''' % {
    'name': user_db.name,
    'link': flask.url_for('user_reset', token=user_db.token, _external=True),
    'brand': config.CONFIG_DB.brand_name,
  }

  flask.flash(
    'A reset link has been sent to your email address.',
    category='success',
  )
  send_mail_notification('Reset your password', body, to)


def activate_user_notification(user_db):
  if not user_db.email:
    return
  user_db.token = util.uuid()
  user_db.put()

  to = user_db.email
  body = '''Welcome to %(brand)s.

Follow the link below to confirm your email address and activate your account:

%(link)s

If it wasn't you, we apologize. You can either ignore this email or reply to it
so we can take a look.

Best regards,
%(brand)s
''' % {
    'link': flask.url_for('user_activate', token=user_db.token, _external=True),
    'brand': config.CONFIG_DB.brand_name,
  }

  flask.flash(
    'An activation link has been sent to your email address.',
    category='success',
  )
  send_mail_notification('Activate your account', body, to)


###############################################################################
# Admin Related
###############################################################################
def email_conflict_notification(email):
  body = 'There is a conflict with %s\n\n%s' % (
    email,
    flask.url_for('user_list', email=email, _external=True),
  )
  send_mail_notification('Conflict with: %s' % email, body)
