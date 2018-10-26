gulp = require('gulp-help') require 'gulp'
requireDir = require('require-dir') './gulp/tasks'
$ = require('gulp-load-plugins')()


gulp.task 'default',
  'Start the local server, watch for changes and reload browser automatically.
  For available options refer to "run" task.',
  $.sequence 'run', ['watch']
