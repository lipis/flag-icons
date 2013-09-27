module.exports = (grunt)->
  SRC_DIR = "less"
  TARGET_DIR = "css"

  grunt.initConfig
    less:
      app_css:
        src: "#{SRC_DIR}/flag-icon.less"
        dest: "#{TARGET_DIR}/flag-icon.css"

    cssmin:
      app_css:
        src: "#{TARGET_DIR}/flag-icon.css"
        dest: "#{TARGET_DIR}/flag-icon.min.css"

    watch:
      css:
        options:
          livereload: true
        files: "#{SRC_DIR}/*.less"
        tasks: ["build"]

      assets:
        options:
          livereload: true
        files: ['index.html', 'assets/*']

    connect:
      server:
        options:
          port: 8000
          keepalive: true


    grunt.loadNpmTasks("grunt-contrib-less")
    grunt.loadNpmTasks("grunt-contrib-cssmin")
    grunt.loadNpmTasks("grunt-contrib-watch")
    grunt.loadNpmTasks('grunt-contrib-connect')

    grunt.registerTask("default", ["build", "watch"])
    grunt.registerTask("build", ["less", "cssmin"])
