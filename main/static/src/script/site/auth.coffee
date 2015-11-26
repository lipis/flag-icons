window.init_auth = ->
  $('.remember').change ->
    buttons = $('.btn-social').toArray().concat $('.btn-social-icon').toArray()
    for button in buttons
      href = $(button).prop 'href'
      if $('.remember input').is ':checked'
        $(button).prop 'href', "#{href}&remember=true"
        $('#remember').prop 'checked', true
      else
        $(button).prop 'href', href.replace '&remember=true', ''
        $('#remember').prop 'checked', false

  $('.remember').change()
