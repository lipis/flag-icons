module.exports = (grunt)->
  less = 'less'
  TARGET_DIR = 'css'

  grunt.initConfig
    less:
      flag:
        src: 'less/flag-icon.less'
        dest: 'css/flag-icon.css'
      docs:
        src: 'assets/docs.less'
        dest: 'assets/docs.css'

    cssmin:
      flag:
        src: 'css/flag-icon.css'
        dest: 'css/flag-icon.min.css'

    watch:
      css:
        options:
          livereload: true
        files: '**/*.less'
        tasks: ['build']

      assets:
        options:
          livereload: true
        files: ['index.html', 'assets/*']

    connect:
      server:
        options:
          port: 8000
          keepalive: true


    grunt.loadNpmTasks 'grunt-contrib-less'
    grunt.loadNpmTasks 'grunt-contrib-cssmin'
    grunt.loadNpmTasks 'grunt-contrib-watch'
    grunt.loadNpmTasks 'grunt-contrib-connect'

    grunt.registerTask 'build',   ['less', 'cssmin']
    grunt.registerTask 'default', ['build', 'watch']
