window.init_user_list = ->
  init_user_selections()
  init_user_delete_btn()
  init_user_merge_btn()


init_user_selections = ->
  $('input[name=user_db]').each ->
    user_select_row $(this)

  $('#select-all').change ->
    $('input[name=user_db]').prop 'checked', $(this).is ':checked'
    $('input[name=user_db]').each ->
      user_select_row $(this)

  $('input[name=user_db]').change ->
    user_select_row $(this)


user_select_row = ($element) ->
  update_user_selections()
  $('input[name=user_db]').each ->
    id = $element.val()
    $("##{id}").toggleClass 'warning', $element.is ':checked'


update_user_selections = ->
  selected = $('input[name=user_db]:checked').length
  $('#user-actions').toggleClass 'hidden', selected == 0
  $('#user-merge').toggleClass 'hidden', selected < 2
  if selected is 0
    $('#select-all').prop 'indeterminate', false
    $('#select-all').prop 'checked', false
  else if $('input[name=user_db]:not(:checked)').length is 0
    $('#select-all').prop 'indeterminate', false
    $('#select-all').prop 'checked', true
  else
    $('#select-all').prop 'indeterminate', true


###############################################################################
# Delete Users Stuff
###############################################################################
init_user_delete_btn = ->
  $('#user-delete').click (e) ->
    clear_notifications()
    e.preventDefault()
    confirm_message = ($(this).data 'confirm').replace '{users}', $('input[name=user_db]:checked').length
    if confirm confirm_message
      user_keys = []
      $('input[name=user_db]:checked').each ->
        $(this).attr 'disabled', true
        user_keys.push $(this).val()
      delete_url = $(this).data 'api-url'
      success_message = $(this).data 'success'
      error_message = $(this).data 'error'
      api_call 'DELETE', delete_url, {user_keys: user_keys.join(',')}, (err, result) ->
        if err
          $('input[name=user_db]:disabled').removeAttr 'disabled'
          show_notification error_message.replace('{users}', user_keys.length), 'danger'
          return
        $("##{result.join(', #')}").fadeOut ->
          $(this).remove()
          update_user_selections()
          show_notification success_message.replace('{users}', user_keys.length), 'success'


###############################################################################
# Merge Users Stuff
###############################################################################
window.init_user_merge = ->
  user_keys = $('#user_keys').val()
  api_url = $('.api-url').data 'api-url'
  api_call 'GET', api_url, {user_keys: user_keys}, (error, result) ->
    if error
      LOG 'Something went terribly wrong'
      return
    window.user_dbs = result
    $('input[name=user_db]').removeAttr 'disabled'

  $('input[name=user_db]').change (event) ->
    user_key = $(event.currentTarget).val()
    select_default_user user_key


select_default_user = (user_key) ->
  $('.user-row').removeClass('success').addClass 'danger'
  $("##{user_key}").removeClass('danger').addClass 'success'

  for user_db in user_dbs
    if user_key == user_db.key
      $('input[name=user_key]').val user_db.key
      $('input[name=username]').val user_db.username
      $('input[name=name]').val user_db.name
      $('input[name=email]').val user_db.email
      break


init_user_merge_btn = ->
  $('#user-merge').click (e) ->
    e.preventDefault()
    user_keys = []
    $('input[name=user_db]:checked').each ->
      user_keys.push $(this).val()
    user_merge_url = $(this).data 'user-merge-url'
    window.location.href = "#{user_merge_url}?user_keys=#{user_keys.join(',')}"
