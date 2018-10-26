gulp = require('gulp-help') require 'gulp'
$ = require('gulp-load-plugins')()
uglify = require('gulp-uglify-es').default
config = require '../config'
paths = require '../paths'
util = require '../util'


is_coffee = (file) ->
  return file.path.indexOf('.coffee') > 0


gulp.task 'script', false, ->
  gulp.src config.script
  .pipe $.plumber errorHandler: util.onError
  .pipe $.if is_coffee, $.coffee()
  .pipe $.concat 'script.js'
  .pipe $.babel presets: ['@babel/env']
  .pipe uglify()
  .pipe $.size {title: 'Minified scripts'}
  .pipe gulp.dest "#{paths.static.min}/script"


gulp.task 'script:dev', false, ->
  gulp.src config.script
  .pipe $.plumber errorHandler: util.onError
  .pipe $.sourcemaps.init()
  .pipe $.if is_coffee, $.coffee()
  .pipe $.concat 'script.js'
  .pipe $.sourcemaps.write()
  .pipe gulp.dest "#{paths.static.dev}/script"
