#!/usr/bin/env python
# coding: utf-8

from datetime import datetime
from distutils import spawn
import argparse
import json
import os
import platform
import shutil
import socket
import sys
import time
import urllib
import urllib2

import main
from main import config


###############################################################################
# Options
###############################################################################
PARSER = argparse.ArgumentParser()
PARSER.add_argument(
    '-w', '--watch', dest='watch', action='store_true',
    help='watch files for changes when running the development web server',
  )
PARSER.add_argument(
    '-c', '--clean', dest='clean', action='store_true',
    help='recompiles files when running the development web server',
  )
PARSER.add_argument(
    '-C', '--clean-all', dest='clean_all', action='store_true',
    help='''Cleans all the pip, Node & Bower related tools / libraries and
    updates them to their latest versions''',
  )
PARSER.add_argument(
    '-m', '--minify', dest='minify', action='store_true',
    help='compiles files into minified version before deploying'
  )
PARSER.add_argument(
    '-s', '--start', dest='start', action='store_true',
    help='starts the dev_appserver.py with storage_path pointing to temp',
  )
PARSER.add_argument(
    '-o', '--host', dest='host', action='store', default='127.0.0.1',
    help='the host to start the dev_appserver.py',
  )
PARSER.add_argument(
    '-p', '--port', dest='port', action='store', default='8080',
    help='the port to start the dev_appserver.py',
  )
PARSER.add_argument(
    '-f', '--flush', dest='flush', action='store_true',
    help='clears the datastore, blobstore, etc',
  )
PARSER.add_argument(
    '--appserver-args', dest='args', nargs=argparse.REMAINDER, default=[],
    help='all following args are passed to dev_appserver.py',
  )
ARGS = PARSER.parse_args()


###############################################################################
# Directories
###############################################################################
DIR_BOWER_COMPONENTS = 'bower_components'
DIR_MAIN = 'main'
DIR_NODE_MODULES = 'node_modules'
DIR_STYLE = 'style'
DIR_SCRIPT = 'script'
DIR_TEMP = 'temp'
DIR_VENV = os.path.join(DIR_TEMP, 'venv')

DIR_STATIC = os.path.join(DIR_MAIN, 'static')

DIR_SRC = os.path.join(DIR_STATIC, 'src')
DIR_SRC_SCRIPT = os.path.join(DIR_SRC, DIR_SCRIPT)
DIR_SRC_STYLE = os.path.join(DIR_SRC, DIR_STYLE)

DIR_DST = os.path.join(DIR_STATIC, 'dst')
DIR_DST_STYLE = os.path.join(DIR_DST, DIR_STYLE)
DIR_DST_SCRIPT = os.path.join(DIR_DST, DIR_SCRIPT)

DIR_MIN = os.path.join(DIR_STATIC, 'min')
DIR_MIN_STYLE = os.path.join(DIR_MIN, DIR_STYLE)
DIR_MIN_SCRIPT = os.path.join(DIR_MIN, DIR_SCRIPT)

DIR_LIB = os.path.join(DIR_MAIN, 'lib')
DIR_LIBX = os.path.join(DIR_MAIN, 'libx')
FILE_LIB = '%s.zip' % DIR_LIB
FILE_LIB_REQUIREMENTS = 'requirements.txt'
FILE_PIP_RUN = os.path.join(DIR_TEMP, 'pip.guard')

DIR_BIN = os.path.join(DIR_NODE_MODULES, '.bin')
FILE_COFFEE = os.path.join(DIR_BIN, 'coffee')
FILE_GRUNT = os.path.join(DIR_BIN, 'grunt')
FILE_LESS = os.path.join(DIR_BIN, 'lessc')
FILE_UGLIFYJS = os.path.join(DIR_BIN, 'uglifyjs')
FILE_VENV = os.path.join(DIR_VENV, 'Scripts', 'activate.bat') \
    if platform.system() is 'Windows' \
    else os.path.join(DIR_VENV, 'bin', 'activate')

DIR_STORAGE = os.path.join(DIR_TEMP, 'storage')
FILE_UPDATE = os.path.join(DIR_TEMP, 'update.json')


###############################################################################
# Other global variables
###############################################################################
REQUIREMENTS_URL = 'http://docs.gae-init.appspot.com/requirement/'


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


def remove_file_dir(file_dir):
  if os.path.exists(file_dir):
    if os.path.isdir(file_dir):
      shutil.rmtree(file_dir)
    else:
      os.remove(file_dir)


def clean_files():
  bad_endings = ['pyc', 'pyo', '~']
  print_out(
      'CLEAN FILES',
      'Removing files: %s' % ', '.join(['*%s' % e for e in bad_endings]),
    )
  for root, _, files in os.walk('.'):
    for filename in files:
      for bad_ending in bad_endings:
        if filename.endswith(bad_ending):
          remove_file_dir(os.path.join(root, filename))


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

  target = source.replace(DIR_SRC_SCRIPT, target_dir).replace('.coffee', '.js')
  if not is_dirty(source, target):
    return
  make_dirs(os.path.dirname(target))
  if not source.endswith('.coffee'):
    print_out('COPYING', source)
    shutil.copy(source, target)
    return
  print_out('COFFEE', source)
  os_execute(FILE_COFFEE, '-cp', source, target)


def compile_style(source, target_dir, check_modified=False):
  if not os.path.isfile(source):
    print_out('NOT FOUND', source)
    return
  if not source.endswith('.less'):
    return

  target = source.replace(DIR_SRC_STYLE, target_dir).replace('.less', '.css')
  if check_modified and not is_style_modified(target):
    return

  minified = ''
  if target_dir == DIR_MIN_STYLE:
    minified = '-x'
    target = target.replace('.css', '.min.css')
    print_out('LESS MIN', source)
  else:
    print_out('LESS', source)

  make_dirs(os.path.dirname(target))
  os_execute(FILE_LESS, minified, source, target)


def make_lib_zip(force=False):
  if force and os.path.isfile(FILE_LIB):
    remove_file_dir(FILE_LIB)
  if not os.path.isfile(FILE_LIB):
    if os.path.exists(DIR_LIB):
      print_out('ZIP', FILE_LIB)
      shutil.make_archive(DIR_LIB, 'zip', DIR_LIB)
    else:
      print_out('NOT FOUND', DIR_LIB)


def is_dirty(source, target):
  if not os.access(target, os.O_RDONLY):
    return True
  return os.stat(source).st_mtime - os.stat(target).st_mtime > 0


def is_style_modified(target):
  for root, _, files in os.walk(DIR_SRC):
    for filename in files:
      path = os.path.join(root, filename)
      if path.endswith('.less') and is_dirty(path, target):
        return True
  return False


def compile_all_dst():
  for source in config.STYLES:
    compile_style(os.path.join(DIR_STATIC, source), DIR_DST_STYLE, True)
  for _, scripts in config.SCRIPTS:
    for source in scripts:
      compile_script(os.path.join(DIR_STATIC, source), DIR_DST_SCRIPT)


def update_path_separators():
  def fixit(path):
    return path.replace('\\', '/').replace('/', os.sep)

  for idx in xrange(len(config.STYLES)):
    config.STYLES[idx] = fixit(config.STYLES[idx])

  for _, scripts in config.SCRIPTS:
    for idx in xrange(len(scripts)):
      scripts[idx] = fixit(scripts[idx])


def listdir(directory, split_ext=False):
  try:
    if split_ext:
      return [os.path.splitext(dir_)[0] for dir_ in os.listdir(directory)]
    else:
      return os.listdir(directory)
  except OSError:
    return []


def site_packages_path():
  if platform.system() == 'Windows':
    return os.path.join(DIR_VENV, 'Lib', 'site-packages')
  py_version = 'python%s.%s' % sys.version_info[:2]
  return os.path.join(DIR_VENV, 'lib', py_version, 'site-packages')


def create_virtualenv(is_windows):
  if not os.path.exists(FILE_VENV):
    os.system('virtualenv --no-site-packages %s' % DIR_VENV)
    os.system('echo %s >> %s' % (
        'set PYTHONPATH=' if is_windows else 'unset PYTHONPATH', FILE_VENV
      ))
    gae_path = find_gae_path()
    pth_file = os.path.join(site_packages_path(), 'gae.pth')
    echo_to = 'echo %s >> {pth}'.format(pth=pth_file)
    os.system(echo_to % gae_path)
    os.system(echo_to % os.path.abspath(DIR_LIBX))
    fix_path_cmd = 'import dev_appserver; dev_appserver.fix_sys_path()'
    os.system(echo_to % (
        fix_path_cmd if is_windows else '"%s"' % fix_path_cmd
      ))
  return True


def exec_pip_commands(command):
  is_windows = platform.system() == 'Windows'
  script = []
  if create_virtualenv(is_windows):
    activate_cmd = 'call %s' if is_windows else 'source %s'
    activate_cmd %= FILE_VENV
    script.append(activate_cmd)

  script.append('echo %s' % command)
  script.append(command)
  script = '&'.join(script) if is_windows else \
      '/bin/bash -c "%s"' % ';'.join(script)
  os.system(script)


def check_pip_should_run():
  if not os.path.exists(FILE_PIP_RUN):
    return True
  return os.path.getmtime(FILE_PIP_RUN) < \
      os.path.getmtime(FILE_LIB_REQUIREMENTS)


def install_py_libs():
  if not check_pip_should_run():
    return

  exec_pip_commands('pip install -q -r %s' % FILE_LIB_REQUIREMENTS)

  exclude_ext = ['.pth', '.pyc', '.egg-info', '.dist-info']
  exclude_prefix = ['setuptools-', 'pip-', 'Pillow-']
  exclude = [
      'test', 'tests', 'pip', 'setuptools', '_markerlib', 'PIL',
      'easy_install.py', 'pkg_resources.py'
    ]

  def _exclude_prefix(pkg):
    for prefix in exclude_prefix:
      if pkg.startswith(prefix):
        return True
    return False

  def _exclude_ext(pkg):
    for ext in exclude_ext:
      if pkg.endswith(ext):
        return True
    return False

  def _get_dest(pkg):
    make_dirs(DIR_LIB)
    return os.path.join(DIR_LIB, pkg)

  site_packages = site_packages_path()
  dir_libs = listdir(DIR_LIB)
  dir_libs.extend(listdir(DIR_LIBX))
  for dir_ in listdir(site_packages):
    if dir_ in dir_libs or dir_ in exclude:
      continue
    if _exclude_prefix(dir_) or _exclude_ext(dir_):
      continue
    src_path = os.path.join(site_packages, dir_)
    copy = shutil.copy if os.path.isfile(src_path) else shutil.copytree
    copy(src_path, _get_dest(dir_))

  with open(FILE_PIP_RUN, 'w') as pip_run:
    pip_run.write('Prevents pip execution if newer than requirements.txt')


def clean_py_libs():
  remove_file_dir(DIR_LIB)
  remove_file_dir(DIR_VENV)


def get_dependencies(file_name):
  with open(file_name) as json_file:
    json_data = json.load(json_file)
  dependencies = json_data.get('dependencies', dict()).keys()
  return dependencies + json_data.get('devDependencies', dict()).keys()


def install_dependencies():
  for dependency in get_dependencies('package.json'):
    if not os.path.exists(os.path.join(DIR_NODE_MODULES, dependency)):
      os.system('npm install')
      break

  for dependency in get_dependencies('bower.json'):
    if not os.path.exists(os.path.join(DIR_BOWER_COMPONENTS, dependency)):
      os.system('"%s" ext' % FILE_GRUNT)
      break

  install_py_libs()


def check_for_update():
  if os.path.exists(FILE_UPDATE):
    mtime = os.path.getmtime(FILE_UPDATE)
    last = datetime.utcfromtimestamp(mtime).strftime('%Y-%m-%d')
    today = datetime.utcnow().strftime('%Y-%m-%d')
    if last == today:
      return
  try:
    request = urllib2.Request(
        'https://gae-init.appspot.com/_s/version/',
        urllib.urlencode({'version': main.__version__}),
      )
    response = urllib2.urlopen(request)
    make_dirs(DIR_TEMP)
    with open(FILE_UPDATE, 'w') as update_json:
      update_json.write(response.read())
  except urllib2.HTTPError:
    pass


def print_out_update():
  try:
    with open(FILE_UPDATE, 'r') as update_json:
      data = json.load(update_json)
    if main.__version__ < data['version']:
      print_out('UPDATE')
      print_out(data['version'], 'Latest version of gae-init')
      print_out(main.__version__, 'Your version is a bit behind')
      print_out('CHANGESET', data['changeset'])
  except (ValueError, KeyError):
    os.remove(FILE_UPDATE)
  except IOError:
    pass


def update_missing_args():
  if ARGS.start or ARGS.clean_all:
    ARGS.clean = True


def uniq(seq):
  seen = set()
  return [e for e in seq if e not in seen and not seen.add(e)]


###############################################################################
# Doctor
###############################################################################
def internet_on():
  try:
    urllib2.urlopen('http://74.125.228.100', timeout=2)
    return True
  except (urllib2.URLError, socket.timeout):
    return False


def check_requirement(check_func):
  result, name, help_url_id = check_func()
  if not result:
    print_out('NOT FOUND', name)
    if help_url_id:
      print 'Please see %s%s' % (REQUIREMENTS_URL, help_url_id)
    return False
  return True


def find_gae_path():
  if platform.system() == 'Windows':
    gae_path = None
    for path in os.environ['PATH'].split(os.pathsep):
      if os.path.isfile(os.path.join(path, 'dev_appserver.py')):
        gae_path = path
  else:
    gae_path = spawn.find_executable('dev_appserver.py')
    if gae_path:
      gae_path = os.path.dirname(os.path.realpath(gae_path))
  if not gae_path:
    return ''
  if not os.path.isfile(os.path.join(gae_path, 'gcloud')):
    return gae_path
  gae_path = os.path.join(gae_path, '..', 'platform', 'google_appengine')
  if os.path.exists:
    return os.path.realpath(gae_path)
  return ''


def check_internet():
  return internet_on(), 'Internet', ''


def check_gae():
  return bool(find_gae_path()), 'Google App Engine SDK', '#gae'


def check_git():
  return bool(spawn.find_executable('git')), 'Git', '#git'


def check_nodejs():
  return bool(spawn.find_executable('node')), 'Node.js', '#nodejs'


def check_pip():
  return bool(spawn.find_executable('pip')), 'pip', '#pip'


def check_virtualenv():
  return bool(spawn.find_executable('virtualenv')), 'virtualenv', '#virtualenv'


def doctor_says_ok():
  checkers = [check_gae, check_git, check_nodejs, check_pip, check_virtualenv]
  if False in [check_requirement(check) for check in checkers]:
    sys.exit(1)
  return check_requirement(check_internet)


###############################################################################
# Main
###############################################################################
def run_clean():
  print_out('CLEAN')
  clean_files()
  make_lib_zip(force=True)
  remove_file_dir(DIR_DST)
  make_dirs(DIR_DST)
  compile_all_dst()
  print_out('DONE')


def run_clean_all():
  print_out('CLEAN ALL')
  remove_file_dir(DIR_BOWER_COMPONENTS)
  remove_file_dir(DIR_NODE_MODULES)
  clean_py_libs()
  clean_files()
  remove_file_dir(FILE_LIB)
  remove_file_dir(FILE_PIP_RUN)


def run_minify():
  print_out('MINIFY')
  clean_files()
  make_lib_zip(force=True)
  remove_file_dir(DIR_MIN)
  make_dirs(DIR_MIN_SCRIPT)

  for source in config.STYLES:
    compile_style(os.path.join(DIR_STATIC, source), DIR_MIN_STYLE)

  for module, scripts in config.SCRIPTS:
    scripts = uniq(scripts)
    coffees = ' '.join([
        os.path.join(DIR_STATIC, script)
        for script in scripts if script.endswith('.coffee')
      ])

    pretty_js = os.path.join(DIR_MIN_SCRIPT, '%s.js' % module)
    ugly_js = os.path.join(DIR_MIN_SCRIPT, '%s.min.js' % module)
    print_out('COFFEE MIN', ugly_js)

    if len(coffees):
      os_execute(FILE_COFFEE, '--join -cp', coffees, pretty_js, append=True)
    for script in scripts:
      if not script.endswith('.js'):
        continue
      script_file = os.path.join(DIR_STATIC, script)
      merge_files(script_file, pretty_js)
    os_execute(FILE_UGLIFYJS, pretty_js, '-cm', ugly_js)
    remove_file_dir(pretty_js)
  print_out('DONE')


def run_watch():
  print_out('WATCHING')
  make_lib_zip()
  make_dirs(DIR_DST)

  compile_all_dst()
  print_out('DONE', 'and watching for changes (Ctrl+C to stop)')
  while True:
    time.sleep(0.5)
    reload(config)
    update_path_separators()
    compile_all_dst()


def run_flush():
  remove_file_dir(DIR_STORAGE)
  print_out('STORAGE CLEARED')


def run_start():
  make_dirs(DIR_STORAGE)
  clear = 'yes' if ARGS.flush else 'no'
  port = int(ARGS.port)
  run_command = '''
      dev_appserver.py %s
      --host %s
      --port %s
      --admin_port %s
      --storage_path=%s
      --clear_datastore=%s
      --skip_sdk_update_check
      %s
    ''' % (DIR_MAIN, ARGS.host, port, port + 1, DIR_STORAGE, clear,
           " ".join(ARGS.args))
  os.system(run_command.replace('\n', ' '))


def run():
  if len(sys.argv) == 1 or (ARGS.args and not ARGS.start):
    PARSER.print_help()
    sys.exit(1)

  os.chdir(os.path.dirname(os.path.realpath(__file__)))

  update_path_separators()
  update_missing_args()

  if ARGS.clean_all:
    run_clean_all()

  if doctor_says_ok():
    install_dependencies()
    check_for_update()

  print_out_update()

  if ARGS.clean:
    run_clean()

  if ARGS.minify:
    run_minify()

  if ARGS.watch:
    run_watch()

  if ARGS.flush:
    run_flush()

  if ARGS.start:
    run_start()


if __name__ == '__main__':
  run()
