gulp = require('gulp')
$ = require('gulp-load-plugins')()
main_bower_files = require 'main-bower-files'
del = require 'del'
exec = require('child_process').exec
minimist = require 'minimist'


root_dir = './main'
static_dir = "#{root_dir}/static"
paths =
  clean: [
      "#{static_dir}/dst"
      "#{static_dir}/ext"
      "#{static_dir}/min"
    ]
  watch: [
      "#{static_dir}/**/*.css"
      "#{static_dir}/**/*.js"
      "#{root_dir}/**/*.html"
      "#{root_dir}/**/*.py"
    ]


run = (option) ->
  proc = exec "python -u run.py -#{option}"
  proc.stderr.on 'data', (data) -> process.stderr.write data
  proc.stdout.on 'data', (data) -> process.stdout.write data


gulp.task 'clean', ->
  del paths.clean

gulp.task 'bower_install', ->
  $.bower()

gulp.task 'ext', ['bower_install'], ->
  gulp.src(main_bower_files(),
    base: 'bower_components'
  ).pipe gulp.dest("#{static_dir}/ext")

gulp.task 'reload', ->
  $.livereload.listen()
  gulp.watch(paths.watch).on 'change', $.livereload.changed

gulp.task 'watch', ->
  run 'w'

gulp.task 'run', ->
  argv = process.argv.slice(2)
  argv_lenght = Object.keys(argv).length
  if argv_lenght <= 1
    run 's'
  else
    known_options =
      default:
        C: false
        c: false
        h: false
        m: false
        s: false
        w: false
    options = minimist argv, known_options
    for k of known_options.default
      if options[k]
        run k
        break

gulp.task 'default', ['reload', 'run', 'watch']
