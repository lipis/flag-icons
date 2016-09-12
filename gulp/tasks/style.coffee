gulp = require('gulp-help') require 'gulp'
$ = require('gulp-load-plugins')()
config = require '../config'
paths = require '../paths'
util = require '../util'


gulp.task 'style', false, ->
  gulp.src config.style
  .pipe $.plumber errorHandler: util.onError
  .pipe $.less()
  .pipe $.cssnano
    discardComments: removeAll: true
    zindex: false
  .pipe $.size {title: 'Minified styles'}
  .pipe gulp.dest "#{paths.static.min}/style"


gulp.task 'style:dev', false, ->
  gulp.src config.style
  .pipe $.plumber errorHandler: util.onError
  .pipe $.sourcemaps.init()
  .pipe $.less()
  .pipe $.autoprefixer {map: true}
  .pipe $.sourcemaps.write()
  .pipe gulp.dest "#{paths.static.dev}/style"
