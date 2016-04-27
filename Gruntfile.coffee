module.exports = (grunt)->
  less = 'less'
  sass = 'sass'
  TARGET_DIR = 'css'

  grunt.initConfig
    less:
      flag:
        src: 'less/flag-icon.less'
        dest: 'css/flag-icon.css'
      docs:
        src: 'assets/docs.less'
        dest: 'assets/docs.css'

    sass:
      flag:
        src: 'sass/flag-icon.scss'
        dest: 'css/flag-icon.css'

    cssmin:
      flag:
        src: 'css/flag-icon.css'
        dest: 'css/flag-icon.min.css'

    watch:
      less:
        options:
          livereload: true
        files: '**/*.less'
        tasks: ['build']

      sass:
        options:
          livereload: true
        files: '**/*.scss'
        tasks: ['build-sass']

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
    grunt.loadNpmTasks 'grunt-contrib-sass'
    grunt.loadNpmTasks 'grunt-contrib-cssmin'
    grunt.loadNpmTasks 'grunt-contrib-watch'
    grunt.loadNpmTasks 'grunt-contrib-connect'

    grunt.registerTask 'build',   ['less', 'cssmin']
    grunt.registerTask 'build-sass',   ['sass', 'cssmin']
    grunt.registerTask 'default', ['build', 'watch']
