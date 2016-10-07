$ ->
  init_common()

$ -> $('html.auth').each ->
  init_auth()

$ -> $('html.user-list').each ->
  init_user_list()

$ -> $('html.user-merge').each ->
  init_user_merge()
