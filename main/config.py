# -*- coding: utf-8 -*-
try:
  # This part is surrounded in try/except because the this config.py file is
  # also used in the build.py script which is used to compile/minify the client
  # side files (*.less, *.coffee, *.js) and is not aware of the GAE
  import model
  CONFIG_DB = model.Config.get_master_db()
  SECRET_KEY = CONFIG_DB.flask_secret_key.encode('ascii')
  LOCALE_DEFAULT = CONFIG_DB.locale
except:
  pass

import os
import operator

CURRENT_VERSION_ID = os.environ.get('CURRENT_VERSION_ID', None)
if os.environ.get('SERVER_SOFTWARE', '').startswith('Google App Engine'):
  DEVELOPMENT = False
else:
  DEVELOPMENT = True

PRODUCTION = not DEVELOPMENT
DEBUG = DEVELOPMENT

DEFAULT_DB_LIMIT = 64

################################################################################
# i18n Stuff
################################################################################

# Languages: http://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
# Countries: http://en.wikipedia.org/wiki/ISO_3166-1
# To Add/Modify languages use one of the filenames in: libx/babel/localedata/
# Examples with country included: en_GB, ru_RU, de_CH
LOCALE = {
  'en': u'English',
  'el': u'Ελληνικά',
  'pl': u'Polski',
  'ru': u'Русский',
}

LOCALE_SORTED = sorted(LOCALE.iteritems(), key=operator.itemgetter(1))

################################################################################
# Client modules, also used by the build.py script.
################################################################################
STYLES = [
    'src/less/style.less',
  ]

SCRIPTS_MODULES = [
    'libs',
    'site',
  ]

SCRIPTS = {
  'libs': [
    'lib/jquery.js',
    'lib/pubnub.js',
    'lib/bootstrap/js/bootstrap-alert.js',
    'lib/bootstrap/js/bootstrap-button.js',
    'lib/bootstrap/js/bootstrap-dropdown.js',
    'lib/bootstrap/js/bootstrap-collapse.js',
  ],
  'site': [
    'src/coffee/common/util.coffee',
    'src/coffee/common/service.coffee',
    'src/coffee/common/common.coffee',
    'src/coffee/common/channel.coffee',

    'src/coffee/site/app.coffee',
    'src/coffee/site/profile.coffee',
    'src/coffee/site/admin.coffee',
  ],
}
