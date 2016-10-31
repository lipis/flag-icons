gulp = require('gulp-help') require 'gulp'
$ = require('gulp-load-plugins')()
paths = require '../paths'


gulp.task 'reload', false, ->
  $.livereload.listen 35729
  $.watch [
    "#{paths.static.dev}/**/*.{css,js}"
    "#{paths.main}/**/*.{html,py}"
  ], events: ['change'], (file) ->
    $.livereload.changed file


gulp.task 'ext_watch_rebuild', false, (callback) ->
  $.sequence('clean:dev', 'copy_bower_files', 'ext:dev', 'style:dev') callback


gulp.task 'watch', false, ->
  $.watch 'requirements.txt', ->
    $.sequence('pip')()
  $.watch 'package.json', ->
    $.sequence('npm')()
  $.watch 'bower.json', ->
    $.sequence('ext_watch_rebuild')()
  $.watch 'gulp/config.coffee', ->
    $.sequence('ext:dev', ['style:dev', 'script:dev'])()
  $.watch paths.static.ext, ->
    $.sequence('ext:dev')()
  $.watch "#{paths.src.script}/**/*.{coffee,js}", ->
    $.sequence('script:dev')()
  $.watch "#{paths.src.style}/**/*.less", ->
    $.sequence('style:dev')()
