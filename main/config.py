try:
  # This part is surrounded in try/except because the this config.py file is
  # also used in the build.py script which is used to compile/minify the client
  # side files (*.less, *.coffee, *.js) and is not aware of the GAE
  import model
  CONFIG_DB = model.Config.get_master_db()
  SECRET_KEY = CONFIG_DB.flask_secret_key.encode('ascii')
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

DEFAULT_DB_LIMIT = 64

################################################################################
# Client modules, also used by the build.py script.
################################################################################
STYLES = [
    'src/less/style.less',
  ]

SCRIPTS_MODULES = [
    'libs',
    'scripts',
  ]

SCRIPTS = {
    'libs': [
      'lib/jquery.js',
      'lib/bootstrap/js/bootstrap-alert.js',
      'lib/bootstrap/js/bootstrap-button.js',
      'lib/bootstrap/js/bootstrap-collapse.js',
      'lib/bootstrap/js/bootstrap-dropdown.js',
    ],
    'scripts': [
      'src/coffee/common/util.coffee',
      'src/coffee/common/service.coffee',
      'src/coffee/common/common.coffee',

      'src/coffee/site/app.coffee',
      'src/coffee/site/profile.coffee',
      'src/coffee/site/admin.coffee',
    ],
  }
