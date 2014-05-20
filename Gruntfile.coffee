module.exports = (grunt) ->
  require('load-grunt-tasks') grunt
  path = require 'path'

  grunt.initConfig
    watch:
      style:
        options:
          livereload: true
        files: 'main/static/**/*.css'

      rest:
        options:
          livereload: true
        files: 'main/**/*.{py,js,html}'

    bower:
      install:
        options:
          targetDir: 'main/static/ext'
          layout: (type, component) ->
            if type.search('/') > -1
              path.join type.replace '/', "/#{component}/"
            else
              path.join type, component

    clean:
      ext: 'main/static/ext'
      min: 'main/static/min'
      dst: 'main/static/dst'

    grunt.registerTask 'default', ['watch']
    grunt.registerTask 'ext', ['clean:ext', 'bower']
