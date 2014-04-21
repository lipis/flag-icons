window.init_announcement = ->
  ($ '.alert-announcement button.close').click ->
    if sessionStorage
      sessionStorage['closedAnnouncement'] = ($ '.alert-announcement').html()

  if sessionStorage and sessionStorage['closedAnnouncement'] == ($ '.alert-announcement').html()
    ($ '.alert-announcement').hide()
