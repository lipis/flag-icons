fs = require 'fs'
gulp = require('gulp-help') require 'gulp'
main_bower_files = require 'main-bower-files'
$ = do require 'gulp-load-plugins'
paths = require '../paths'


gulp.task 'npm', false, ->
  gulp.src 'package.json'
  .pipe $.plumber()
  .pipe do $.start


gulp.task 'bower', false, ->
  cmd = 'node_modules/.bin/bower install'
  if /^win/.test process.platform
    cmd = cmd.replace /\//g, '\\'
  start_map = [{match: /bower.json$/, cmd: cmd}]
  gulp.src 'bower.json'
  .pipe $.plumber()
  .pipe $.start start_map


gulp.task 'copy_bower_files', false, ['bower'], ->
  gulp.src do main_bower_files, base: paths.dep.bower_components
  .pipe gulp.dest paths.static.ext


gulp.task 'pip', false, ->
  gulp.src('run.py').pipe $.start [{match: /run.py$/, cmd: 'python run.py -d'}]


gulp.task 'zip', false, ->
  fs.exists paths.py.lib_file, (exists) ->
    if not exists
      fs.exists paths.py.lib, (exists) ->
        if exists
          gulp.src "#{paths.py.lib}/**"
          .pipe $.plumber()
          .pipe $.zip 'lib.zip'
          .pipe gulp.dest paths.main


gulp.task 'init', false, $.sequence 'pip', 'copy_bower_files'
