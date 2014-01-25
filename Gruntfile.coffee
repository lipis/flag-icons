module.exports = (grunt)->
  grunt.initConfig
    watch:
      style:
        options:
          livereload: true
        files: 'main/static/**/*.css'

      rest:
        options:
          livereload: true
        files: [
            'main/**/*.py'
            'main/**/*.js'
            'main/**/*.html'
          ]

    grunt.loadNpmTasks('grunt-contrib-watch')
    grunt.registerTask('default', ['watch'])
