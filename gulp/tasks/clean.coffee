del = require 'del'
gulp = require('gulp-help') require 'gulp'
paths = require '../paths'


gulp.task 'clean',
  'Clean project from temporarty files, generated CSS & JS and compiled Python
  files.', ['clean:dev'], ->
    del './**/*.pyc'
    del './**/*.pyo'
    del './**/*.~'


gulp.task 'clean:dev', false, ->
  del [paths.static.dev, paths.static.ext, paths.static.min]


gulp.task 'clean:venv', false, ->
  del [paths.py.lib, paths.py.lib_file]
  del paths.dep.py
  del paths.dep.py_guard


gulp.task 'reset',
  'Complete reset of project. Run "npm install" after this procedure.',
  ['clean', 'clean:dev', 'clean:venv'], ->
    del [paths.dep.bower_components, paths.dep.node_modules]


gulp.task 'flush', 'Clear local datastore, blobstore, etc.', ->
  del paths.temp.storage
