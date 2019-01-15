# coding: utf-8

import importlib
import pkg_resources


MODULES = [
  'blinker',
  'flask',
  'flask-login|flask_login',
  'flask-oauthlib|flask_oauthlib',
  'flask-restful|flask_restful.__version__',
  'flask-wtf|flask_wtf',
  'jinja2',
  'pyjwt|jwt',
  'unidecode',
  'webargs',
]


def get_module_version(spec):
  names = spec.split('|', 1)
  try:
    module = importlib.import_module(names[-1])
  except:
    return (names[0], 'ERROR: Cannot import')
  try:
    version = module.__version__
  except:
    version = 'n/a'
  return (names[0], version)


def get_versions(working_set=True):
  versions = [get_module_version(name) for name in MODULES]
  if working_set:
    for pkg in pkg_resources.working_set:
      name, version = str(pkg).split(' ', 1)
      versions.append(('{} *'.format(name), version))
  versions.sort()
  return versions
