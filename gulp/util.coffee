$ = require('gulp-load-plugins')()


onError = (err) ->
  $.util.beep()
  console.log err
  this.emit 'end'


module.exports = {onError}
