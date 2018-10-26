# coding: utf-8

import os
import sys
import tempfile

from path_util import sys_path_insert

tempfile.SpooledTemporaryFile = tempfile.TemporaryFile

if os.environ.get('SERVER_SOFTWARE', '').startswith('Google App Engine'):
  sys_path_insert('lib.zip')
else:
  if os.name == 'nt':
    os.name = None
    sys.platform = ''

  import re
  from google.appengine.tools.devappserver2.python import runtime

  re_ = runtime.stubs.FakeFile._skip_files.pattern.replace('|^lib/.*', '')
  re_ = re.compile(re_)
  runtime.stubs.FakeFile._skip_files = re_
  sys_path_insert('lib')

sys_path_insert('libx')


def webapp_add_wsgi_middleware(app):
  from google.appengine.ext.appstats import recording
  app = recording.appstats_wsgi_middleware(app)
  return app
