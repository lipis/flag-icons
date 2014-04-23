window.init_announcement = ->
  ($ '.alert-announcement button.close').click ->
    sessionStorage?.setItem 'closedAnnouncement', ($ '.alert-announcement').html()

  if sessionStorage?.getItem('closedAnnouncement') == ($ '.alert-announcement').html()
    ($ '.alert-announcement').hide()
