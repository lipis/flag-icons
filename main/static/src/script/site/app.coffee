$ ->
  init_common()

$ -> ($ 'html.welcome').each ->
  LOG('init welcome')

$ -> ($ 'html.profile').each ->
  init_profile()

$ -> ($ 'html.feedback').each ->

$ -> ($ 'html.user').each ->
  init_user()

$ -> ($ 'html.admin-config').each ->
  init_admin_config()

