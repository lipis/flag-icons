$ ->
  init_common()

$ -> ($ 'html.welcome').each ->
  LOG('init welcome')

$ -> ($ 'html.profile').each ->
  init_profile()

$ -> ($ 'html.feedback').each ->

$ -> ($ 'html.admin-config').each ->
  init_admin_config()
