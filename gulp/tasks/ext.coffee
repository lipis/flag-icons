gulp = require('gulp-help') require 'gulp'
$ = require('gulp-load-plugins')()
uglify = require('gulp-uglify-es').default
config = require '../config'
paths = require '../paths'
util = require '../util'


gulp.task 'ext', false, ->
  gulp.src config.ext
  .pipe $.plumber errorHandler: util.onError
  .pipe $.concat 'ext.js'
  .pipe uglify()
  .pipe $.size {title: 'Minified ext libs'}
  .pipe gulp.dest "#{paths.static.min}/script"


gulp.task 'ext:dev', false, ->
  gulp.src config.ext
  .pipe $.plumber errorHandler: util.onError
  .pipe $.sourcemaps.init()
  .pipe $.concat 'ext.js'
  .pipe $.sourcemaps.write()
  .pipe gulp.dest "#{paths.static.dev}/script"
