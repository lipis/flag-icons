flagIcon = require './flag-icon'

module.exports = (grunt)->
  less = 'less'
  TARGET_DIR = 'css'

  grunt.initConfig
    template:
      options:
        data: flagIcon
      less:
        files:
          'less/flag-icon-list.less': 'less/flag-icon-list.less.tpl'
          'less/flag-icon-more.less': 'less/flag-icon-more.less.tpl'
      sass:
        files:
          'sass/_flag-icon-list.scss': 'sass/_flag-icon-list.scss.tpl'
          'sass/_flag-icon-more.scss': 'sass/_flag-icon-more.scss.tpl'
      html:
        files:
          'index.html': 'index.html.tpl'
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
    grunt.loadNpmTasks 'grunt-template'
    grunt.loadNpmTasks 'grunt-contrib-watch'
    grunt.loadNpmTasks 'grunt-contrib-connect'

    grunt.registerTask 'build',   ['template', 'less', 'cssmin']
    grunt.registerTask 'default', ['build', 'watch']
