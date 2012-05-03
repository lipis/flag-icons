import os

CURRENT_VERSION_ID = os.environ.get('CURRENT_VERSION_ID', None)
if os.environ.get('SERVER_SOFTWARE', '').startswith('Google App Engine'):
  DEVELOPMENT = False
else:
  DEVELOPMENT = True

DEBUG = DEVELOPMENT
PRODUCTION = not DEVELOPMENT

BRAND_NAME = 'GAE Init'
#This is for Flask Sessions (read more http://goo.gl/rXrMk)
SECRET_KEY = '908e41b104d5c1e023d4747165db4ba7'

#External providers on dev environment. Please change.
ANALYTICS_ID = ''
FACEBOOK_APP_ID = ''
FACEBOOK_APP_SECRET = ''

TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET = ''

#To use these variables on production. Please change.
if PRODUCTION:
  FACEBOOK_APP_ID = ''
  FACEBOOK_APP_SECRET = ''
  ANALYTICS_ID = ''

#default limit for services
DEFAULT_DB_LIMIT = 64


################################################################################
# CLient modules, also used by the build.py script.
################################################################################
STYLES = set(['src/style/style.less'])

SCRIPTS_MODULES = [
    'libs',
    'site',
  ]

SCRIPTS = {
  'libs': [
    'lib/jquery.js',
    'lib/bootstrap/js/bootstrap-alert.js',
    'lib/bootstrap/js/bootstrap-button.js',
  ],
  'site': [
    'src/common/util.coffee',
    'src/common/service.coffee',
    'src/common/common.coffee',

    'src/site/app.coffee',
    'src/site/profile.coffee',
  ],
}
