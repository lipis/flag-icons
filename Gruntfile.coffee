module.exports = (grunt)->
  SRC_DIR = "less"
  TARGET_DIR = "css"

  grunt.initConfig
    clean:
      main:
        src: TARGET_DIR

    less:
      app_css:
        src: "#{SRC_DIR}/country-flag-icons.less"
        dest: "#{TARGET_DIR}/country-flag-icons.css"

    cssmin:
      app_css:
        src: "#{TARGET_DIR}/country-flag-icons.css"
        dest: "#{TARGET_DIR}/country-flag-icons.min.css"

    watch:
      build:
        options:
          base: SRC_DIR
          keepalive: true
        files: ["#{SRC_DIR}/**/*.less"]
        tasks: ["less"]
      css:
        options:
          livereload: true
        files: "#{TARGET_DIR}/country-flag-icons.css"
      html_templates:
        options:
          livereload: true
        files: 'index.html'


    grunt.loadNpmTasks("grunt-contrib-clean")
    grunt.loadNpmTasks("grunt-contrib-less")
    grunt.loadNpmTasks("grunt-contrib-cssmin")
    grunt.loadNpmTasks("grunt-contrib-watch")

    grunt.registerTask("default", ["build", "watch"])
    grunt.registerTask("build", ["clean", "less"])
    grunt.registerTask("dist", ["clean", "less", "cssmin"])
