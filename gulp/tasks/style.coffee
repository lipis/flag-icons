gulp = require('gulp-help') require 'gulp'
$ = do require 'gulp-load-plugins'
config = require '../config'
paths = require '../paths'
util = require '../util'


gulp.task 'style', false, ->
  gulp.src config.style
  .pipe $.plumber errorHandler: util.onError
  .pipe do $.less
  .pipe $.autoprefixer {cascade: false}
  .pipe do $.minifyCss
  .pipe $.size {title: 'Minified styles'}
  .pipe gulp.dest "#{paths.static.min}/style"


gulp.task 'style:dev', false, ->
  gulp.src config.style
  .pipe $.plumber errorHandler: util.onError
  .pipe do $.sourcemaps.init
  .pipe do $.less
  .pipe $.autoprefixer {map: true}
  .pipe do $.sourcemaps.write
  .pipe gulp.dest "#{paths.static.dev}/style"
