################################################################################
# Logging
################################################################################
window.LOG = (args) ->
  return if not window.console?.log?
  ar = arguments
  switch ar.length
    when 0 then return
    when 1 then window.console.log(ar[0])
    when 2 then window.console.log(ar[0], ar[1])
    when 3 then window.console.log(ar[0], ar[1], ar[2])
    when 4 then window.console.log(ar[0], ar[1], ar[2], ar[3])
    when 5 then window.console.log(ar[0], ar[1], ar[2], ar[3], ar[4])
    when 6 then window.console.log(ar[0], ar[1], ar[2], ar[3], ar[4], ar[5])
    else window.console.log("Too many arguments to LOG")


################################################################################
# Helpers
################################################################################
window.init_loading_button = () ->
  $('body').on 'click', '.btn-loading', ->
    $(this).button('loading')
