window.init_loading_button = () ->
  $('body').on 'click', '.btn-loading', ->
    $(this).button('loading')
