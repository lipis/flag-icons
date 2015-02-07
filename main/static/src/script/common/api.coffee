window.api_call = (method, url, params, data, callback) ->
  callback = callback || data || params
  data = data || params
  if arguments.length == 4
    data = undefined
  if arguments.length ==  3
    params = undefined
    data = undefined
  params = params || {}
  for k, v of params
    delete params[k] if not v?
  separator = if url.search('\\?') >= 0 then '&' else '?'
  $.ajax
    type: method
    url: "#{url}#{separator}#{$.param params}"
    contentType: 'application/json'
    accepts: 'application/json'
    dataType: 'json'
    data: if data then JSON.stringify(data) else undefined
    success: (data) ->
      if data.status == 'success'
        more = undefined
        if data.next_url
          more = (callback) -> api_call(method, data.next_url, {}, callback)
        callback? undefined, data.result, more
      else
        callback? data
    error: (jqXHR, textStatus, errorThrown) ->
      error =
        error_code: 'ajax_error'
        text_status: textStatus
        error_thrown: errorThrown
        jqXHR: jqXHR
      try
        error = $.parseJSON(jqXHR.responseText) if jqXHR.responseText
      catch e
        error = error
      LOG 'api_call error', error
      callback? error
