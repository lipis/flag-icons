module.exports = (grunt)->
  TARGET_DIR = "css"

  grunt.initConfig
    less:
      app_css:
        src: "less/flag-icon.less"
        dest: "#{TARGET_DIR}/flag-icon.css"

    sass:
      app_css:
        src: "sass/flag-icon.{sass,scss}"
        dest: "#{TARGET_DIR}/flag-icon.css"
        options:
          sourcemap: 'none'
          style: 'expanded'

    cssmin:
      app_css:
        src: "#{TARGET_DIR}/flag-icon.css"
        dest: "#{TARGET_DIR}/flag-icon.min.css"

    watch:
      options:
        livereload: true

      less:
        files: "less/*.less"
        tasks: ["less", "cssmin"]

      sass:
        files: "sass/*.{sass,scss}"
        tasks: ["sass", "cssmin"]

      assets:
        files: ['index.html', 'assets/*']

    connect:
      server:
        options:
          port: 8000
          keepalive: true

    grunt.loadNpmTasks("grunt-contrib-cssmin")
    grunt.loadNpmTasks("grunt-contrib-less")
    grunt.loadNpmTasks("grunt-contrib-sass")
    grunt.loadNpmTasks("grunt-contrib-cssmin")
    grunt.loadNpmTasks("grunt-contrib-watch")
    grunt.loadNpmTasks('grunt-contrib-connect')

    grunt.registerTask("default", ["build", "watch"])
    grunt.registerTask("build", ["less", "sass", "cssmin"])
