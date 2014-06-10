window.init_signin = ->
  $('.remember').change ->
    for button in $('.btn-social')
      href = $(button).attr 'href'
      if $('.remember input').is ':checked'
        $(button).attr 'href', "#{href}&remember=true"
      else
        $(button).attr 'href', href.replace('&remember=true', '')

  $('.remember').change()
