gulp = require('gulp-help') require 'gulp'
browserSync = require('browser-sync')
$ = require('gulp-load-plugins')()
config = require '../config'
paths = require '../paths'


gulp.task 'browser-sync', false, ->
  browserSync.init
    proxy: "#{config.host}:#{config.port}"
    notify: false
  $.watch [
    "#{paths.static.dev}/**/*.{css,js}"
    "#{paths.main}/**/*.{html,py}"
  ], events: ['change'], (file) ->
    browserSync.reload()


gulp.task 'ext_watch_rebuild', false, (callback) ->
  $.sequence('clean:dev', 'copy_bower_files', 'ext:dev', 'style:dev') callback


gulp.task 'watch', false, ->
  $.watch 'requirements.txt', ->
    $.sequence('pip')()
  $.watch 'package.json', ->
    $.sequence('yarn')()
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
