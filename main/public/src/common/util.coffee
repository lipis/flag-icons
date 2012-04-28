# ==============================================================================
# Logging
# ==============================================================================
window.LOG = (args) ->
  return if !window.console
  return if !window.console.log
  if arguments.length == 0
    return
  if arguments.length == 1
    window.console.log(arguments[0])
  else if arguments.length == 2
    window.console.log(arguments[0], arguments[1])
  else if arguments.length == 3
    window.console.log(arguments[0], arguments[1], arguments[2])
  else if arguments.length == 4
    window.console.log(arguments[0], arguments[1], arguments[2], arguments[3])
  else if arguments.length == 5
    window.console.log(arguments[0], arguments[1], arguments[2], arguments[3], arguments[4])
  else
    window.console.log("Too many arguments to LOG function")
