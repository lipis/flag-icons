from flask.ext import wtf
from flask import _request_ctx_stack
from flask.ext.babel import get_locale
from babel import support
import os


def translations_path():
  module_path = os.path.abspath(__file__)
  dirname = os.path.join(os.path.dirname(module_path), 'translations')
  return dirname


def _get_translations():
  try:
    ctx = _request_ctx_stack.top
    translations = getattr(ctx, 'wtforms_translations', None)
    if translations is None:
      translations = support.Translations.load(
        translations_path(), [get_locale()], domain='messages'
      )
      ctx.wtforms_translations = translations
    return translations
  except:
    return None


class Translations(object):
  def gettext(self, string):
    t = _get_translations()
    if t is None:
      return string
    return t.ugettext(string)

  def ngettext(self, singular, plural, n):
    t = _get_translations()
    if t is None:
      if n == 1:
        return singular
      return plural
    return t.ungettext(singular, plural, n)


translations = Translations()


class Form(wtf.Form):
  def _get_translations(self):
    return translations
