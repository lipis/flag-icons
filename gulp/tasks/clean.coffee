del = require 'del'
gulp = require('gulp-help') require 'gulp'
paths = require '../paths'


gulp.task 'clean',
'Clean the project from temp files, Python compiled files
and minified styles and scripts.', ['clean:dev'], ->
  del './**/*.pyc'
  del './**/*.pyo'
  del './**/*.~'


gulp.task 'clean:dev', false, ->
  del [paths.static.dev, paths.static.ext, paths.static.min]


gulp.task 'clean:venv', false, ->
  del [paths.py.lib, paths.py.lib_file]
  del paths.dep.py
  del paths.dep.py_guard


gulp.task 'initial',
'Complete cleaning the project: cleans all the
Pip requirements, temp files, Node & Bower related tools and libraries.',
['clean', 'clean:venv'], ->
  del [paths.dep.bower_components, paths.dep.node_modules]


gulp.task 'flush', 'Clears the datastore, blobstore, etc', ->
  del paths.temp.storage

