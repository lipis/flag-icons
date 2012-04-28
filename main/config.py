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
FACEBOOK_APP_ID = '280140768742767'
FACEBOOK_APP_SECRET = '434375dd129f13f41824bb0037c3df50'

TWITTER_CONSUMER_KEY = 'SaB3iBCEM25nU8u2DpA7g'
TWITTER_CONSUMER_SECRET = 'EmUOu1JptJd5ES9a2lGkn1UBDRxIMtr2Vs8GIk'

#To use these variables on production. Please change.
if PRODUCTION:
  FACEBOOK_APP_ID = '345959722128319'
  FACEBOOK_APP_SECRET = 'e277a51e913a7aa296410161d31530cb'
  ANALYTICS_ID = 'UA-12558606-5'

#default limit for services
DEFAULT_DB_LIMIT = 64


################################################################################
# CLient modules, also used by the build.py script.
################################################################################
SCRIPTS_MODULES = [
    'libs',
    'site',
  ]

STYLES = set(['src/style/style.less'])

SCRIPTS = {
  'libs': [
    'lib/jquery.js',
    'lib/bootstrap/js/bootstrap-alert.js',
  ],
  'site': [
    'src/common/util.coffee',
    'src/common/service.coffee',
    'src/site/app.coffee',
  ],
}
