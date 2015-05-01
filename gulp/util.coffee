$ = do require 'gulp-load-plugins'

onError = (err) ->
  do $.util.beep
  console.log err
  this.emit 'end'

module.exports = {onError}
