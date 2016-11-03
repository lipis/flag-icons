#!/usr/bin/env python
# coding: utf-8

from datetime import datetime
import argparse
import HTMLParser
import json
import os
import sys
import urllib2


###############################################################################
# Options
###############################################################################
MAGIC_URL = 'http://magic.gae-init.appspot.com'

PARSER = argparse.ArgumentParser(description='Visit %s for more.' % MAGIC_URL)
PARSER.add_argument(
  '-p', '--project', dest='project_id', action='store',
  help='project ID of the project that you want to sync',
)
PARSER.add_argument(
  '-r', '--remote', dest='remote_url', action='store', default=MAGIC_URL,
  help="set the remote URL if it's not http://magic.gae-init.appspot.com",
)
ARGS = PARSER.parse_args()


###############################################################################
# Constants
###############################################################################
DIR_MAIN = 'main'

DIR_CONTROL = os.path.join(DIR_MAIN, 'control')
FILE_CONTROL_INIT = os.path.join(DIR_CONTROL, '__init__.py')

DIR_MODEL = os.path.join(DIR_MAIN, 'model')
FILE_MODEL_INIT = os.path.join(DIR_MODEL, '__init__.py')

DIR_API = os.path.join(DIR_MAIN, 'api', 'v1')
FILE_API_INIT = os.path.join(DIR_API, '__init__.py')

DIR_TEMPLATES = os.path.join(DIR_MAIN, 'templates')
FILE_HEADER = os.path.join(DIR_TEMPLATES, 'bit', 'header.html')
FILE_ADMIN = os.path.join(DIR_TEMPLATES, 'admin', 'admin.html')


###############################################################################
# Helpers
###############################################################################
def print_out(script, filename=''):
  timestamp = datetime.now().strftime('%H:%M:%S')
  if not filename:
    filename = '-' * 46
    script = script.rjust(12, '-')
  print '[%s] %12s %s' % (timestamp, script, filename)


def make_dirs(directory):
  directory = os.path.dirname(directory)
  if not os.path.exists(directory):
    os.makedirs(directory)


def append_to(project_url, destination):
  url = ('%smagic/%s' % (project_url, destination)).replace('\\', '/')
  response = urllib2.urlopen(url)
  if response.getcode() == 200:
    with open(destination, 'r') as dest:
      lines = ''.join(dest.readlines())
      content = response.read()
      if content in lines:
        print_out('IGNORED', destination)
        return

    with open(destination, 'a') as dest:
      dest.write(content)
      print_out('APPEND', destination)


def safe_text(text):
  return (HTMLParser.HTMLParser().unescape(text.decode('utf8'))).encode('utf8')


def insert_to(project_url, destination, find_what, indent=0):
  url = ('%smagic/%s' % (project_url, destination)).replace('\\', '/')
  response = urllib2.urlopen(url)
  if response.getcode() == 200:
    with open(destination, 'r') as dest:
      dest_contents = dest.readlines()
      lines = ''.join(dest_contents)
      content = safe_text(response.read())
      if content.replace(' ', '') in lines.replace(' ', ''):
        print_out('IGNORED', destination)
        return

    generated = []
    for line in dest_contents:
      generated.append(line)
      if line.lower().find(find_what.lower()) >= 0:
        spaces = len(line) - len(line.lstrip())
        for l in content.split('\n'):
          if l:
            generated.append('%s%s\n' % (' ' * (spaces + indent), l))

    with open(destination, 'w') as dest:
      for line in generated:
        dest.write(line)
      print_out('INSERT', destination)


def create_file(project_url, destination):
  make_dirs(destination)
  url = ('%smagic/%s' % (project_url, destination)).replace('\\', '/')
  response = urllib2.urlopen(url)
  if response.getcode() == 200:
    with open(destination, 'w') as dest:
      dest.write(safe_text(response.read()))
      dest.write('\n')
      print_out('CREATE', destination)


def get_project_db():
  url = '%s/api/v1/project/%s/' % (ARGS.remote_url, ARGS.project_id.split('/')[0])
  response = urllib2.urlopen(url)
  if response.getcode() == 200:
    project_body = response.read()
    project_db = json.loads(project_body)['result']
    project_db['project_url'] = url
    return project_db
  return None


def sync_from_magic(project_db):
  model_dbs = {}
  project_url = project_db['project_url']
  model_url = '%smodel/' % project_url

  response = urllib2.urlopen(model_url)
  if response.getcode() == 200:
    models_body = response.read()
    model_dbs = json.loads(models_body)['result']

  print_out('UPDATING')
  append_to(project_url, FILE_MODEL_INIT)
  append_to(project_url, FILE_CONTROL_INIT)
  append_to(project_url, FILE_API_INIT)
  insert_to(project_url, FILE_HEADER, '<ul class="nav navbar-nav">', 2)
  insert_to(project_url, FILE_ADMIN, "url_for('user_list'")

  for index, model_db in enumerate(model_dbs):
    print_out('%d of %d' % (index + 1, project_db['model_count']))
    name = model_db['variable_name']
    create_file(project_url, os.path.join(DIR_MODEL, '%s.py' % name))
    create_file(project_url, os.path.join(DIR_CONTROL, '%s.py' % name))
    create_file(project_url, os.path.join(DIR_API, '%s.py' % name))

    root = os.path.join(DIR_TEMPLATES, name)
    create_file(project_url, os.path.join(root, 'admin_%s_update.html' % name))
    create_file(project_url, os.path.join(root, 'admin_%s_list.html' % name))

    if not model_db['admin_only']:
      create_file(project_url, os.path.join(root, '%s_update.html' % name))
      if model_db['public_view']:
        create_file(project_url, os.path.join(root, '%s_view.html' % name))
        create_file(project_url, os.path.join(root, '%s_list.html' % name))


###############################################################################
# Main
###############################################################################
def magic():
  if len(sys.argv) == 1:
    PARSER.print_help()
    sys.exit(1)

  os.chdir(os.path.dirname(os.path.realpath(__file__)))

  if ARGS.project_id:
    project_db = get_project_db()
    answer = raw_input(
      'Are you sure you want to sync "%(name)s" with %(model_count)d '
      'model(s) that was modified on %(modified)s? (Y/n): '
      % {
        'name': project_db['name'],
        'model_count': project_db['model_count'],
        'modified': project_db['modified'][:16].replace('T', ' at '),
      }
    )
    if not answer or answer.lower() == 'y':
      sync_from_magic(project_db)
  else:
    print 'Project ID is not provided.'
    PARSER.print_help()


if __name__ == '__main__':
  magic()
