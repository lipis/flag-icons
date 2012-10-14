#!/usr/bin/env python
import optparse
import os
import config
import time
from datetime import datetime
import shutil


parser = optparse.OptionParser()
parser.add_option('-w', '--watch', dest='watch', action='store_true')
parser.add_option('-c', '--clean', dest='clean', action='store_true')
(options, args) = parser.parse_args()


def print_out(script, filename=''):
  timestamp = datetime.now().strftime('%H:%M:%S')
  print '[%s] %12s %s' % (timestamp, script, filename)


def clean_files():
  print_out("CLEAN FILES", 'Remove "*.pyc" files')
  os.system('find . -name "*.pyc" -print0 | xargs -0 rm -rf')
  print_out("CLEAN FILES", 'Remove "*.*~" files')
  os.system('find . -name "*.*~" -print0 | xargs -0 rm -rf')


def compile_coffee(source, to):
  target = source.replace('/src/', '/%s/' % to).replace('coffee', 'js')
  if not is_dirty(source, target):
    return
  os.system('mkdir -p %s' % os.path.dirname(target))
  if not source.endswith('.coffee'):
    print_out('COPYING', source)
    os.system('cp %s %s' % (source, target))
    return
  print_out('COFFEE', source)
  os.system('node_modules/.bin/coffee -c -p %s > %s' % (source, target))


def compile_less(source, to, check_modified=False):
  target = source.replace('/src/', '/%s/' % to).replace('less', 'css')
  minified = ''
  if not source.endswith('.less'):
    return
  if check_modified and not is_less_modified(target):
    return

  if to == 'min':
    minified = '-x'
    target = target.replace('/style/', '/').replace('.css', '.min.css')
    print_out('LESS MIN', source)
  else:
    print_out('LESS', source)

  os.system('mkdir -p %s' % os.path.dirname(target))
  os.system('node_modules/.bin/lessc %s %s > %s' % (minified, source, target))


def make_lib_zip(force=False):
  if force:
    os.system('rm -f lib.zip')
  if not os.path.isfile('lib.zip'):
    print_out('ZIP', 'Compress libs')
    shutil.make_archive('lib', 'zip', 'lib')


def is_dirty(source, target):
  if not os.access(target, os.O_RDONLY):
    return True
  return os.stat(source).st_mtime - os.stat(target).st_mtime > 0


def is_less_modified(target):
  for folder, folders, files in os.walk('static/src'):
    for file_ in files:
      path = os.path.join(folder, file_)
      if path.endswith('.less') and is_dirty(path, target):
        return True
  return False


def compile_all():
  for source in config.STYLES:
    compile_less('static/%s' % source, 'dst', True)
  for module in config.SCRIPTS:
    for source in config.SCRIPTS[module]:
      compile_coffee('static/%s' % source, 'dst')


if options.watch or options.clean:
  if options.clean:
    os.system("rm -rf static/dst")
    make_lib_zip(force=True)
  else:
    make_lib_zip()
  os.system("mkdir -p static/dst")

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
  os.system("rm -rf static/min")
  os.system("mkdir -p static/min/js")
  for source in config.STYLES:
    compile_less('static/%s' % source, 'min')
  for module in config.SCRIPTS:
    coffees = ' '.join(['static/%s' % script
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
