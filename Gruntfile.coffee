module.exports = (grunt)->
  path = require('path')
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
          targetDir: 'main/static/src/vendor'
          cleanTargetDir: true
          layout: (type, component) ->
            if type is 'fonts'
              path.join '../../vendor-fonts'
            else
              path.join type, component

    grunt.loadNpmTasks('grunt-contrib-watch')
    grunt.registerTask('default', ['watch'])
    grunt.loadNpmTasks('grunt-bower-task')
