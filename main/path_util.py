# coding: utf-8

import os
import pkgutil
import sys


def path_package_path(deps_path, shadow_pkgs):
  sys.path.insert(0, deps_path)
  for _, pkg, ispkg in pkgutil.iter_modules():
    if ispkg and pkg in shadow_pkgs:
      global_pkg = __import__(pkg)
      global_pkg.__path__.insert(0, '%s/%s' % (deps_path, pkg))


def is_shadowing(package_name):
  try:
    __import__(os.path.splitext(package_name)[0])
    return True
  except ImportError:
    pass
  return False


def get_shadows_zip(filename):
  import zipfile

  shadow_pkgs = set()
  with zipfile.ZipFile(filename) as lib_zip:
    already_test = []
    for fname in lib_zip.namelist():
      pname, fname = os.path.split(fname)
      if fname or (pname and fname):
        continue
      if pname not in already_test and '/' not in pname:
        already_test.append(pname)
        if is_shadowing(pname):
          shadow_pkgs.add(pname)
  return shadow_pkgs


def get_shadows_dir(dirname):
  shadow_pkgs = set()
  if not os.path.exists(dirname):
    return shadow_pkgs
  for pkg in os.listdir(dirname):
    if not pkg == '__init__.py' and os.path.isfile(pkg) and is_shadowing(pkg):
      shadow_pkgs.add(pkg)
  return shadow_pkgs


def sys_path_insert(dirname):
  if dirname.endswith('.zip'):
    path_package_path(dirname, get_shadows_zip(dirname))
  else:
    path_package_path(dirname, get_shadows_dir(dirname))
