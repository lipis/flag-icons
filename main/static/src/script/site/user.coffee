window.init_user = ->
  init_user_selections()
  init_user_delete_btn()


init_user_selections = ->
  ($ 'input[name=user_db]').each ->
    user_select_row ($ this)

  ($ '#select-all').change ->
    ($ 'input[name=user_db]').prop 'checked', ($ this).is ':checked'
    ($ 'input[name=user_db]').each ->
      user_select_row ($ this)

  ($ 'input[name=user_db]').change ->
    user_select_row ($ this)


user_select_row = ($element) ->
  update_selections()
  ($ 'input[name=user_db]').each ->
    id = $element.val()
    ($ "##{id}").toggleClass 'warning', $element.is ':checked'


update_selections = ->
  selected = ($ 'input[name=user_db]:checked').length
  ($ '#user-actions').toggleClass 'hidden', selected == 0
  ($ '#user-merge').parent().toggleClass 'hidden', selected <= 1
  if selected is 0
    ($ '#select-all').prop 'indeterminate', false
    ($ '#select-all').prop 'checked', false
  else if ($ 'input[name=user_db]:not(:checked)').length is 0
    ($ '#select-all').prop 'indeterminate', false
    ($ '#select-all').prop 'checked', true
  else
    ($ '#select-all').prop 'indeterminate', true


init_user_delete_btn = ->
  ($ '#user-delete').click (e) ->
    clear_notifications()
    e.preventDefault()
    confirm_message = (($ this).data 'confirm').replace '{users}', ($ 'input[name=user_db]:checked').length
    if confirm confirm_message
      user_keys = []
      ($ 'input[name=user_db]:checked').each ->
        ($ this).attr 'disabled', true
        user_keys.push ($ this).val()
      delete_url = ($ this).data 'service-url'
      success_message = ($ this).data 'success'
      error_message = ($ this).data 'error'
      service_call 'DELETE', delete_url, {user_keys: user_keys.join(',')}, (err, result) ->
        if err
          ($ 'input[name=user_db]:disabled').removeAttr 'disabled'
          show_notification error_message.replace('{users}', user_keys.length), 'danger'
          return
        ($ "##{result.join(', #')}").fadeOut ->
          ($ this).remove()
          update_selections()
          show_notification success_message.replace('{users}', user_keys.length), 'success'
