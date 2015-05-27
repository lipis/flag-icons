gulp = require('gulp-help') require 'gulp'
$ = do require 'gulp-load-plugins'
paths = require '../paths'


gulp.task 'reload', false, ->
  do $.livereload.listen
  gulp.watch([
    "#{paths.static.root}/dev/style/*.css"
    "#{paths.static.root}/dev/script/*.js"
    "#{paths.main}/**/*.html"
    "#{paths.main}/**/*.py"
  ]).on 'change', $.livereload.changed


gulp.task 'ext_watch_rebuild', false, (callback) ->
  $.sequence('copy_bower_files', 'ext:dev', 'style:dev') callback


gulp.task 'watch', false, ->
  gulp.watch 'requirements.txt', ['pip']
  gulp.watch 'package.json', ['npm']
  gulp.watch 'bower.json', ['ext_watch_rebuild']
  gulp.watch 'gulp/config.coffee', ['style:dev', 'script:dev']
  gulp.watch paths.static.ext, ['ext:dev']
  gulp.watch "#{paths.src.script}/**/*.coffee", ['script:dev']
  gulp.watch "#{paths.src.style}/**/*.less", ['style:dev']
