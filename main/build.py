#!/usr/bin/env python
from datetime import datetime
import argparse
import config
import os
import shutil
import sys
import time

################################################################################
# Options
################################################################################
parser = argparse.ArgumentParser()
parser.add_argument('-w', '--watch', dest='watch', action='store_true',
    help='watch files for changes when running the development web server',
  )
parser.add_argument('-c', '--clean', dest='clean', action='store_true',
    help='recompiles files when running the development web server',
  )
parser.add_argument('-m', '--minify', dest='minify', action='store_true',
    help='compiles files into minified version before deploying'
  )
parser.add_argument('-r', '--run', dest='run', action='store_true',
    help='runs the dev_appserver.py with datastore and blobstore paths',
  )
parser.add_argument('-o', '--host', dest='host', action='store', default='127.0.0.1',
    help='the host to run for the dev_appserver.py',
  )
parser.add_argument('-p', '--port', dest='port', action='store', default='8080',
    help='the port to run for the dev_appserver.py',
  )
args = parser.parse_args()

################################################################################
# Directories
################################################################################
DIR_STATIC = 'static'
DIR_SRC = 'src'
DIR_LESS = 'less'
DIR_COFFEE = 'coffee'
DIR_CSS = 'css'
DIR_JS = 'js'
DIR_MIN = 'min'
DIR_DST = 'dst'
DIR_LIB = 'lib'
DIR_NODE_MODULES = 'node_modules'
DIR_BIN = '.bin'
DIR_TEMP = 'temp'

FILE_ZIP = '%s.zip' % DIR_LIB
FILE_COFFEE = 'coffee'
FILE_LESS = 'lessc'
FILE_UGLIFYJS = 'uglifyjs'


root = os.path.dirname(os.path.realpath(__file__))
dir_static = os.path.join(root, DIR_STATIC)

dir_src = os.path.join(dir_static, DIR_SRC)
dir_src_coffee = os.path.join(dir_src, DIR_COFFEE)
dir_src_less = os.path.join(dir_src, DIR_LESS)

dir_dst = os.path.join(dir_static, DIR_DST)
dir_dst_css = os.path.join(dir_dst, DIR_CSS)
dir_dst_js = os.path.join(dir_dst, DIR_JS)

dir_min = os.path.join(dir_static, DIR_MIN)
dir_min_css = os.path.join(dir_min, DIR_CSS)
dir_min_js = os.path.join(dir_min, DIR_JS)

dir_lib = os.path.join(root, DIR_LIB)
file_lib = os.path.join(root, FILE_ZIP)

dir_bin = os.path.join(root, DIR_NODE_MODULES, DIR_BIN)
file_coffee = os.path.join(dir_bin, FILE_COFFEE)
file_less = os.path.join(dir_bin, FILE_LESS)
file_uglifyjs = os.path.join(dir_bin, FILE_UGLIFYJS)

dir_temp = os.path.join(root, '..', DIR_TEMP)


################################################################################
# Helpers
################################################################################
def print_out(script, filename=''):
  timestamp = datetime.now().strftime('%H:%M:%S')
  if not filename:
    filename = '-' * 41
    script = script.rjust(12, '-')
  print '[%s] %12s %s' % (timestamp, script, filename.replace(root, ''))


def make_dirs(directory):
  if not os.path.exists(directory):
    os.makedirs(directory)


def remove_dir(directory):
  if os.path.isdir(directory):
    shutil.rmtree(directory)


def clean_files():
  bad_endings = ['pyc', '~']
  print_out(
      'CLEAN FILES',
      'Removing files: %s' % ', '.join(['*%s' % e for e in bad_endings]),
    )
  for home, dirs, files in os.walk(root):
    for f in files:
      for b in bad_endings:
        if f.endswith(b):
          os.remove(os.path.join(home, f))


def merge_files(source, target):
  fout = open(target, 'a')
  for line in open(source):
    fout.write(line)
  fout.close()


def os_execute(executable, params, source, target, append=False):
  operator = '>>' if append else '>'
  os.system('"%s" %s %s %s %s' % (executable, params, source, operator, target))


def compile_coffee(source, target_dir):
  target = source.replace(dir_src_coffee, target_dir).replace('.coffee', '.js')
  if not is_dirty(source, target):
    return
  make_dirs(os.path.dirname(target))
  if not source.endswith('.coffee'):
    print_out('COPYING', source)
    shutil.copy(source, target)
    return
  print_out('COFFEE', source)
  os_execute(file_coffee, '-cp', source, target)


def compile_less(source, target_dir, check_modified=False):
  target = source.replace(dir_src_less, target_dir).replace('.less', '.css')
  minified = ''
  if not source.endswith('.less'):
    return
  if check_modified and not is_less_modified(target):
    return

  if target_dir == dir_min_css:
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
    shutil.make_archive(DIR_LIB, 'zip', dir_lib)


def is_dirty(source, target):
  if not os.access(target, os.O_RDONLY):
    return True
  return os.stat(source).st_mtime - os.stat(target).st_mtime > 0


def is_less_modified(target):
  for folder, folders, files in os.walk(dir_src):
    for file_ in files:
      path = os.path.join(folder, file_)
      if path.endswith('.less') and is_dirty(path, target):
        return True
  return False


def compile_all_dst():
  for source in STYLES:
    compile_less(os.path.join(dir_static, source), dir_dst_css, True)
  for module in config.SCRIPTS:
    for source in config.SCRIPTS[module]:
      compile_coffee(os.path.join(dir_static, source), dir_dst_js)


def update_path_separators():
  def fixit(path):
    return path.replace('\\', '/').replace('/', os.sep)

  for idx in xrange(len(STYLES)):
    STYLES[idx] = fixit(STYLES[idx])

  for module in SCRIPTS:
    for idx in xrange(len(SCRIPTS[module])):
      SCRIPTS[module][idx] = fixit(SCRIPTS[module][idx])


def install_dependencies():
  missing = ''
  if not os.path.exists(file_coffee):
    missing += 'coffee-script@1 '
  if not os.path.exists(file_less):
    missing += 'less@1 '
  if not os.path.exists(file_uglifyjs):
    missing += 'uglify-js@1 '

  if missing:
    os.system('npm install %s' % missing)

################################################################################
# Main
################################################################################
SCRIPTS = config.SCRIPTS
STYLES = config.STYLES

os.chdir(root)

update_path_separators()
install_dependencies()

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
  make_dirs(dir_min_js)

  for source in STYLES:
    compile_less(os.path.join(dir_static, source), dir_min_css)

  for module in config.SCRIPTS:
    coffees = ' '.join([os.path.join(dir_static, script)
        for script in config.SCRIPTS[module] if script.endswith('.coffee')
      ])

    pretty_js = os.path.join(dir_min_js, '%s.js' % module)
    ugly_js = os.path.join(dir_min_js, '%s.min.js' % module)
    print_out('COFFEE MIN', ugly_js)

    if len(coffees):
      os_execute(file_coffee, '--join -cp', coffees, pretty_js, append=True)
    for script in config.SCRIPTS[module]:
      if not script.endswith('.js'):
        continue
      script_file = os.path.join(dir_static, script)
      merge_files(script_file, pretty_js)
    os_execute(file_uglifyjs, '-nc', pretty_js, ugly_js)
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
    compile_all_dst()

if args.run:
  dir_datastore = os.path.join(dir_temp, 'datastore')
  dir_blobstore = os.path.join(dir_temp, 'blobstore')
  make_dirs(dir_blobstore)
  os.system(
       '''dev_appserver.py %s \\
          --host %s \\
          --port %s \\
          --datastore_path=%s \\
          --blobstore_path=%s \\
          --skip_sdk_update_check \\
          ''' % (
          root, args.host, args.port, dir_datastore, dir_blobstore,
        )
    )
