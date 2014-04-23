window.init_announcement = ->
  ($ '.alert-announcement button.close').click ->
    sessionStorage?['closedAnnouncement'] = ($ '.alert-announcement').html()

  if sessionStorage?['closedAnnouncement'] == ($ '.alert-announcement').html()
    ($ '.alert-announcement').hide()
