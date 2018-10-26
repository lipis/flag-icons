# -*- coding: utf-8 -*-

import os

from babel import support
from flask import _request_ctx_stack
import flask_babel
import flask_wtf


def _get_translations():
  ctx = _request_ctx_stack.top
  root = os.path.dirname(os.path.abspath(__file__))
  translations_path = os.path.join(root, 'translations')
  translations = support.Translations.load(
      translations_path, [flask_babel.get_locale()], domain='messages'
    )
  ctx.wtforms_translations = translations
  return translations


class Translations(object):
  def gettext(self, string):
    t = _get_translations()
    return string if t is None else t.ugettext(string)

  def ngettext(self, singular, plural, n):
    t = _get_translations()
    if t is None:
      return singular if n == 1 else plural
    return t.ungettext(singular, plural, n)


translations = Translations()


class Form(flask_wtf.FlaskForm):
  def _get_translations(self):
    return translations
