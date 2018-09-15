window.apiCall = function(method, url, params, data, callback) {
  callback = callback || data || params;
  data = data || params;
  if (arguments.length === 4) {
    data = void 0;
  }
  if (arguments.length === 3) {
    params = void 0;
    data = void 0;
  }
  params = params || {};
  for (const key in params) {
    if (params[key] == null) {
      delete params[key];
    }
  }
  const separator = url.search('\\?') >= 0 ? '&' : '?';
  $.ajax({
    accepts: 'application/json',
    contentType: 'application/json',
    data: data ? JSON.stringify(data) : void 0,
    dataType: 'json',
    error(jqXHR, textStatus, errorThrown) {
      let error = {
        error_code: 'ajax_error',
        error_thrown: errorThrown,
        jqXHR,
        text_status: textStatus,
      };
      try {
        if (jqXHR.responseText) {
          error = $.parseJSON(jqXHR.responseText);
        }
      } catch (_error) {
        error = _error;
      }
      LOG('apiCall error', error);
      return typeof callback === 'function' ? callback(error) : void 0;
    },
    success(data_) {
      if (data_.status === 'success') {
        let more = void 0;
        if (data_.next_url) {
          more = callback_ => apiCall(method, data_.next_url, {}, callback);
        }
        return typeof callback === 'function'
          ? callback(void 0, data_.result, more)
          : void 0;
      }
      return typeof callback === 'function' ? callback(data) : void 0;
    },
    type: method,
    url: `${url}${separator}${$.param(params)}`,
  });
};
