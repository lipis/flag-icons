$ ->
  LOG('app init')

$ -> $('html.welcome').each ->
  LOG('init welcome')

$ -> $('html.profile').each ->
  init_profile()

$ -> $('html.admin-config').each ->
  init_admin_config()
