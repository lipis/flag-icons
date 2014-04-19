window.init_announcement = ->
  ($ '.alert-announcement button.close').click (e) ->
    if sessionStorage
      sessionStorage['closedAnnouncement'] = ($ '.alert-announcement').html()

  if sessionStorage and sessionStorage['closedAnnouncement'] == ($ '.alert-announcement').html()
    LOG 'announcement hidden'
  else
    ($ '.alert-announcement').show()
