#JS enabled pages
$ ->
  LOG('app init')

$ -> $('html.welcome').each ->
  LOG('init welcome')

$ -> $('html.profile').each ->
  init_profile()

$ -> $('html.feedback').each ->
  init_loading_button()

$ -> $('html.admin-config').each ->
  init_admin_config()

#Channel Enabled pages
$ ->
  channel_name = $('html').data('channel-name')

  if channel_name == 'chat'
    subscribe_chat()
