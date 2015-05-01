gulp = require('gulp-help') require 'gulp'
requireDir = require('require-dir') './gulp/tasks'
$ = do require 'gulp-load-plugins'

gulp.task 'default',
  'Start the dev_appserver.py, watching changes and LiveReload.
  Available options - please see "run" task.',
  $.sequence 'run', ['watch', 'reload']
