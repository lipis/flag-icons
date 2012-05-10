try:
  # This part is surrounded in try/except because the this config.py file is
  # also used in the build.py script which is used to compile/minify the client
  # side files (*.less, *.coffee, *.js) and is not aware of the GAE
  import model
  ANALYTICS_ID = model.Config.get_master_db().analytics_id
  FACEBOOK_APP_ID = model.Config.get_master_db().facebook_app_id
  FACEBOOK_APP_SECRET = model.Config.get_master_db().facebook_app_secret
  TWITTER_CONSUMER_KEY = model.Config.get_master_db().twitter_consumer_key
  TWITTER_CONSUMER_SECRET = model.Config.get_master_db().twitter_consumer_secret
except:
  pass

import os
CURRENT_VERSION_ID = os.environ.get('CURRENT_VERSION_ID', None)
if os.environ.get('SERVER_SOFTWARE', '').startswith('Google App Engine'):
  DEVELOPMENT = False
else:
  DEVELOPMENT = True

PRODUCTION = not DEVELOPMENT
DEBUG = DEVELOPMENT

BRAND_NAME = 'GAE Init'
#This is for Flask Sessions (read more http://goo.gl/rXrMk)
SECRET_KEY = '908e41b104d5c1e023d4747165db4ba7'

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
