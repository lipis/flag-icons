gulp = require('gulp-help') require 'gulp'
$ = require('gulp-load-plugins')()
paths = require '../paths'


gulp.task 'reload', false, ->
  $.livereload.listen 35729
  gulp.watch([
    "#{paths.static.dev}/**/*.{css,js}"
    "#{paths.main}/**/*.{html,py}"
  ]).on 'change', $.livereload.changed


gulp.task 'ext_watch_rebuild', false, (callback) ->
  $.sequence('clean:dev', 'copy_bower_files', 'ext:dev', 'style:dev') callback


gulp.task 'watch', false, ->
  gulp.watch 'requirements.txt', ['pip']
  gulp.watch 'package.json', ['npm']
  gulp.watch 'bower.json', ['ext_watch_rebuild']
  gulp.watch 'gulp/config.coffee', ['ext:dev', 'style:dev', 'script:dev']
  gulp.watch paths.static.ext, ['ext:dev']
  gulp.watch "#{paths.src.script}/**/*.{coffee,js}", ['script:dev']
  gulp.watch "#{paths.src.style}/**/*.less", ['style:dev']
