#!/usr/bin/env python
import optparse
import os
import config
import time
from datetime import datetime
import shutil

DIR_STATIC = 'static'
DIR_SRC = 'src'
DIR_LESS = 'less'
DIR_COFFEE = 'coffee'
DIR_CSS = 'css'
DIR_JS = 'js'
DIR_MIN = 'min'
DIR_DST = 'dst'
DIR_LIB = 'lib'
FILE_ZIP = '%s.zip' % DIR_LIB

parser = optparse.OptionParser()
parser.add_option('-w', '--watch', dest='watch', action='store_true')
parser.add_option('-c', '--clean', dest='clean', action='store_true')
(options, args) = parser.parse_args()


def print_out(script, filename=''):
  timestamp = datetime.now().strftime('%H:%M:%S')
  print '[%s] %12s %s' % (timestamp, script, filename.replace(root, ''))


def make_dirs(directory):
  if not os.path.exists(directory):
    os.makedirs(directory)


def clean_files():
  print_out('CLEAN FILES', 'Remove "*.pyc" files')
  os.system('find . -name "*.pyc" -print0 | xargs -0 rm -rf')
  print_out('CLEAN FILES', 'Remove "*.*~" files')
  os.system('find . -name "*.*~" -print0 | xargs -0 rm -rf')


def compile_coffee(source, to):
  target = source.replace(dir_src, to).replace('coffee', 'js')
  if not is_dirty(source, target):
    return
  make_dirs(os.path.dirname(target))
  if not source.endswith('.coffee'):
    print_out('COPYING', source)
    os.system('cp %s %s' % (source, target))
    return
  print_out('COFFEE', source)
  os.system('node_modules/.bin/coffee -c -p %s > %s' % (source, target))


def compile_less(source, to, check_modified=False):
  target = source.replace(dir_src, to).replace('less', 'css')
  minified = ''
  if not source.endswith('.less'):
    return
  if check_modified and not is_less_modified(target):
    return

  if to == dir_min:
    minified = '-x'
    target = target.replace('.css', '.min.css')
    print_out('LESS MIN', source)
  else:
    print_out('LESS', source)

  make_dirs(os.path.dirname(target))
  os.system('node_modules/.bin/lessc %s %s > %s' % (minified, source, target))


def make_lib_zip(force=False):
  if force:
    if os.path.isfile(file_lib):
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


def compile_all():
  for source in config.STYLES:
    compile_less(os.path.join(dir_static, source), dir_dst, True)
  for module in config.SCRIPTS:
    for source in config.SCRIPTS[module]:
      compile_coffee(os.path.join(dir_static, source), dir_dst)


root = os.path.dirname(os.path.realpath(__file__))
dir_static = os.path.join(root, DIR_STATIC)
dir_src = os.path.join(dir_static, DIR_SRC)
dir_dst = os.path.join(dir_static, DIR_DST)
dir_min = os.path.join(dir_static, DIR_MIN)
dir_lib = os.path.join(root, DIR_LIB)
file_lib = os.path.join(root, FILE_ZIP)

if options.watch or options.clean:
  if options.clean:
    if os.path.isdir(dir_dst):
      shutil.rmtree(dir_dst)
    make_lib_zip(force=True)
  else:
    make_lib_zip()
  make_dirs(dir_dst)

  compile_all()
  if options.watch:
    print_out('DONE', 'and watching for changes (ctrl+c to stop).')
    while True:
      time.sleep(0.5)
      compile_all()
  else:
    print_out('DONE')

else:
  clean_files()
  make_lib_zip(force=True)
  if os.path.isdir(dir_min):
    shutil.rmtree(dir_min)
  make_dirs(os.path.join(dir_min, DIR_JS))

  for source in config.STYLES:
    compile_less(os.path.join(dir_static, source), dir_min)

  for module in config.SCRIPTS:
    coffees = ' '.join([os.path.join(dir_static, script)
        for script in config.SCRIPTS[module] if script.endswith('.coffee')
      ])
    print_out('COFFEE MIN', '%s.js' % module)
    if len(coffees):
      os.system(
          'node_modules/.bin/coffee --join -c -p %s >> static/min/js/%s.js' % (
          coffees, module,
        ))
    for script in config.SCRIPTS[module]:
      if not script.endswith('.js'):
        continue
      os.system('cat static/%s >> static/min/js/%s.js' % (script, module))

    os.system(
        'node_modules/.bin/uglifyjs -nc static/min/js/%s.js > static/min/js/%s.min.js' % (
        module, module,
      ))
    os.system('rm static/min/js/%s.js' % module)
