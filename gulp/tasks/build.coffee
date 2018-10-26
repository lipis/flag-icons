gulp = require('gulp-help') require 'gulp'
yargs = require 'yargs-parser'
$ = require('gulp-load-plugins')()
config = require '../config'
paths = require '../paths'


gulp.task 'build',
  "Build project to prepare it for a deployment. Minify CSS & JS files and pack
  Python dependencies into #{paths.py.lib_file}.",
  $.sequence 'clean:min', 'init', 'ext', ['script', 'style', 'zip']


gulp.task 'rebuild',
  'Re-build project from scratch. Equivalent to "reset" and "build" tasks.',
  $.sequence 'reset', 'build'


gulp.task 'deploy',
  'Deploy project to Google App Engine. Available options:', ['build'], ->
    options = yargs process.argv, configuration:
      'boolean-negation': false
      'camel-case-expansion': false
    delete options['_']
    options_str = ''
    dryrun = ''
    for k of options
      if k == 'dryrun'
        dryrun = 'echo DRYRUN - would run: '
      else
        if options[k] == true
          options[k] = ''
        options_str += " #{if k.length > 1 then '-' else ''}-#{k} #{options[k]}"

    gulp.src('run.py').pipe $.start [{
      match: /run.py$/
      cmd: "#{dryrun}gcloud app deploy main/*.yaml#{options_str}"
    }]
  ,  options:
      'dryrun': 'run all preparations but do not actually deploy'


gulp.task 'run',
  'Start the local server. Available options:\n
  -o HOST  - the host to start the dev_appserver.py\n
  -p PORT  - the port to start the dev_appserver.py\n
  -a="..." - all following args are passed to dev_appserver.py\n', ->
    $.sequence('init', ['ext:dev', 'script:dev', 'style:dev']) ->
      argv = process.argv.slice 2

      known_options =
        default:
          p: ''
          o: ''
          a: ''

      options = yargs(argv)
      options_str = '-s'
      for k of known_options.default
        if options[k]
          if k == 'a'
            options_str += " --appserver-args \"#{options[k]}\""
          else
            options_str += " -#{k} #{options[k]}"

      if options['p']
        config.port = options['p']
      if options['o']
        config.host = options['o']

      gulp.start('browser-sync')
      gulp.src('run.py').pipe $.start [{
        match: /run.py$/
        cmd: "python run.py #{options_str}"
      }]
