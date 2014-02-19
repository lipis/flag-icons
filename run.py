#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import argparse
import json
import os
import shutil
import sys
import time

from main import config


###############################################################################
# Options
###############################################################################
parser = argparse.ArgumentParser()
parser.add_argument(
    '-w', '--watch', dest='watch', action='store_true',
    help='watch files for changes when running the development web server',
  )
parser.add_argument(
    '-c', '--clean', dest='clean', action='store_true',
    help='''recompiles files when running the development web server, but
    obsolete if -s is used''',
  )
parser.add_argument(
    '-m', '--minify', dest='minify', action='store_true',
    help='compiles files into minified version before deploying'
  )
parser.add_argument(
    '-s', '--start', dest='start', action='store_true',
    help='starts the dev_appserver.py with storage_path pointing to temp',
  )
parser.add_argument(
    '-o', '--host', dest='host', action='store', default='127.0.0.1',
    help='the host to start the dev_appserver.py',
  )
parser.add_argument(
    '-p', '--port', dest='port', action='store', default='8080',
    help='the port to start the dev_appserver.py',
  )
parser.add_argument(
    '-f', '--flush', dest='flush', action='store_true',
    help='clears the datastore, blobstore, etc',
  )
args = parser.parse_args()


###############################################################################
# Directories
###############################################################################
DIR_MAIN = 'main'
DIR_STATIC = 'static'
DIR_SRC = 'src'
DIR_STYLE = 'style'
DIR_SCRIPT = 'script'
DIR_MIN = 'min'
DIR_DST = 'dst'
DIR_LIB = 'lib'
DIR_NODE_MODULES = 'node_modules'
DIR_BIN = '.bin'
DIR_TEMP = 'temp'
DIR_STORAGE = 'storage'

FILE_ZIP = '%s.zip' % DIR_LIB
FILE_COFFEE = 'coffee'
FILE_LESS = 'lessc'
FILE_UGLIFYJS = 'uglifyjs'

dir_static = os.path.join(DIR_MAIN, DIR_STATIC)

dir_src = os.path.join(dir_static, DIR_SRC)
dir_src_script = os.path.join(dir_src, DIR_SCRIPT)
dir_src_style = os.path.join(dir_src, DIR_STYLE)

dir_dst = os.path.join(dir_static, DIR_DST)
dir_dst_style = os.path.join(dir_dst, DIR_STYLE)
dir_dst_script = os.path.join(dir_dst, DIR_SCRIPT)

dir_min = os.path.join(dir_static, DIR_MIN)
dir_min_style = os.path.join(dir_min, DIR_STYLE)
dir_min_script = os.path.join(dir_min, DIR_SCRIPT)

dir_lib = os.path.join(DIR_MAIN, DIR_LIB)
file_lib = os.path.join(DIR_MAIN, FILE_ZIP)

dir_bin = os.path.join(DIR_NODE_MODULES, DIR_BIN)
file_coffee = os.path.join(dir_bin, FILE_COFFEE)
file_less = os.path.join(dir_bin, FILE_LESS)
file_uglifyjs = os.path.join(dir_bin, FILE_UGLIFYJS)

dir_storage = os.path.join(DIR_TEMP, DIR_STORAGE)


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
  if not os.path.exists(directory):
    os.makedirs(directory)


def remove_dir(directory):
  if os.path.isdir(directory):
    shutil.rmtree(directory)


def clean_files():
  bad_endings = ['pyc', 'pyo', '~']
  print_out(
      'CLEAN FILES',
      'Removing files: %s' % ', '.join(['*%s' % e for e in bad_endings]),
    )
  for home, dirs, files in os.walk('.'):
    for f in files:
      for b in bad_endings:
        if f.endswith(b):
          os.remove(os.path.join(home, f))


def merge_files(source, target):
  fout = open(target, 'a')
  for line in open(source):
    fout.write(line)
  fout.close()


def os_execute(executable, args, source, target, append=False):
  operator = '>>' if append else '>'
  os.system('"%s" %s %s %s %s' % (executable, args, source, operator, target))


def compile_script(source, target_dir):
  if not os.path.isfile(source):
    print_out('NOT FOUND', source)
    return

  target = source.replace(dir_src_script, target_dir).replace('.coffee', '.js')
  if not is_dirty(source, target):
    return
  make_dirs(os.path.dirname(target))
  if not source.endswith('.coffee'):
    print_out('COPYING', source)
    shutil.copy(source, target)
    return
  print_out('COFFEE', source)
  os_execute(file_coffee, '-cp', source, target)


def compile_style(source, target_dir, check_modified=False):
  if not os.path.isfile(source):
    print_out('NOT FOUND', source)
    return

  target = source.replace(dir_src_style, target_dir).replace('.less', '.css')
  minified = ''
  if not source.endswith('.less'):
    return
  if check_modified and not is_style_modified(target):
    return

  if target_dir == dir_min_style:
    minified = '-x'
    target = target.replace('.css', '.min.css')
    print_out('LESS MIN', source)
  else:
    print_out('LESS', source)

  make_dirs(os.path.dirname(target))
  os_execute(file_less, minified, source, target)


def make_lib_zip(force=False):
  if force and os.path.isfile(file_lib):
    os.remove(file_lib)
  if not os.path.isfile(file_lib):
    print_out('ZIP', file_lib)
    shutil.make_archive(dir_lib, 'zip', dir_lib)


def is_dirty(source, target):
  if not os.access(target, os.O_RDONLY):
    return True
  return os.stat(source).st_mtime - os.stat(target).st_mtime > 0


def is_style_modified(target):
  for folder, folders, files in os.walk(dir_src):
    for file_ in files:
      path = os.path.join(folder, file_)
      if path.endswith('.less') and is_dirty(path, target):
        return True
  return False


def compile_all_dst():
  for source in config.STYLES:
    compile_style(os.path.join(dir_static, source), dir_dst_style, True)
  for module in config.SCRIPTS:
    for source in config.SCRIPTS[module]:
      compile_script(os.path.join(dir_static, source), dir_dst_script)


def update_path_separators():
  def fixit(path):
    return path.replace('\\', '/').replace('/', os.sep)

  for idx in xrange(len(config.STYLES)):
    config.STYLES[idx] = fixit(config.STYLES[idx])

  for module in config.SCRIPTS:
    for idx in xrange(len(config.SCRIPTS[module])):
      config.SCRIPTS[module][idx] = fixit(config.SCRIPTS[module][idx])


def install_dependencies():
  missing = False
  if not os.path.exists(file_coffee):
    missing = True
  if not os.path.exists(file_less):
    missing = True
  if not os.path.exists(file_uglifyjs):
    missing = True
  if not os.path.exists(os.path.join(DIR_NODE_MODULES, 'grunt')):
    missing = True
  try:
    file_package = os.path.join(DIR_NODE_MODULES, 'uglify-js', 'package.json')
    package_json = json.load(open(file_package))
    version = package_json['version']
    if int(version.split('.')[0]) < 2:
      missing = True
  except:
    missing = True

  if missing:
    os.system('npm install')


def update_missing_args():
  if args.start:
    args.clean = True


def uniq(seq):
  seen = set()
  return [e for e in seq if e not in seen and not seen.add(e)]


###############################################################################
# Main
###############################################################################
os.chdir(os.path.dirname(os.path.realpath(__file__)))

update_path_separators()
install_dependencies()
update_missing_args()

if len(sys.argv) == 1:
  parser.print_help()
  sys.exit(1)

if args.clean:
  print_out('CLEAN')
  clean_files()
  make_lib_zip(force=True)
  remove_dir(dir_dst)
  make_dirs(dir_dst)
  compile_all_dst()
  print_out('DONE')

if args.minify:
  print_out('MINIFY')
  clean_files()
  make_lib_zip(force=True)
  remove_dir(dir_min)
  make_dirs(dir_min_script)

  for source in config.STYLES:
    compile_style(os.path.join(dir_static, source), dir_min_style)

  for module in config.SCRIPTS:
    scripts = uniq(config.SCRIPTS[module])
    coffees = ' '.join([
        os.path.join(dir_static, script)
        for script in scripts if script.endswith('.coffee')
      ])

    pretty_js = os.path.join(dir_min_script, '%s.js' % module)
    ugly_js = os.path.join(dir_min_script, '%s.min.js' % module)
    print_out('COFFEE MIN', ugly_js)

    if len(coffees):
      os_execute(file_coffee, '--join -cp', coffees, pretty_js, append=True)
    for script in scripts:
      if not script.endswith('.js'):
        continue
      script_file = os.path.join(dir_static, script)
      merge_files(script_file, pretty_js)
    os_execute(file_uglifyjs, pretty_js, '-cm', ugly_js)
    os.remove(pretty_js)
  print_out('DONE')

if args.watch:
  print_out('WATCHING')
  make_lib_zip()
  make_dirs(dir_dst)

  compile_all_dst()
  print_out('DONE', 'and watching for changes (Ctrl+C to stop)')
  while True:
    time.sleep(0.5)
    reload(config)
    update_path_separators()
    compile_all_dst()

if args.flush:
  remove_dir(dir_storage)
  print_out('STORAGE CLEARED')

if args.start:
  make_dirs(dir_storage)
  clear = 'yes' if args.flush else 'no'
  port = int(args.port)
  run_command = '''
      dev_appserver.py %s
      --host %s
      --port %s
      --admin_port %s
      --storage_path=%s
      --clear_datastore=%s
      --skip_sdk_update_check
    ''' % (DIR_MAIN, args.host, port, port + 1, dir_storage, clear)
  os.system(run_command.replace('\n', ' '))
