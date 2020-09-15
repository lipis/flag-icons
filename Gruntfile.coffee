module.exports = (grunt)->
  less = 'less'
  TARGET_DIR = 'css'

  grunt.initConfig
    less:
      flag:
        src: 'less/flag-icon.less'
        dest: 'css/flag-icon.css'
      flag1x1:
        src: 'less/flag-icon-1x1.less'
        dest: 'css/flag-icon-1x1.css'
      flag4x3:
        src: 'less/flag-icon-4x3.less'
        dest: 'css/flag-icon-4x3.css'
      docs:
        src: 'assets/docs.less'
        dest: 'assets/docs.css'

    cssmin:
      flag:
        src: 'css/flag-icon.css'
        dest: 'css/flag-icon.min.css'
      flag1x1:
        src: 'css/flag-icon-1x1.css'
        dest: 'css/flag-icon-1x1.min.css'
      flag4x3:
        src: 'css/flag-icon-4x3.css'
        dest: 'css/flag-icon-4x3.min.css'

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
