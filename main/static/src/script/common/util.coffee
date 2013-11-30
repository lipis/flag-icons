window.LOG = ->
  console?.log? arguments...


window.init_common = ->
  init_loading_button()
  init_time()


window.init_loading_button = ->
  ($ 'body').on 'click', '.btn-loading', ->
    ($ this).button 'loading'


window.init_time = ->
  if ($ 'time').length > 0
    recalculate = ->
      ($ 'time[datetime]').each ->
        date = moment.utc ($ this).attr 'datetime'
        diff = moment().diff date , 'days'
        if diff > 25
          ($ this).text date.local().format 'YYYY-MM-DD'
        else
          ($ this).text date.fromNow()
        ($ this).attr 'title', date.local().format 'dddd, MMMM Do YYYY, HH:mm:ss Z'
      setTimeout arguments.callee, 1000 * 45
    recalculate()


window.clear_notifications = ->
  ($ '#notifications').empty()


window.show_notification = (message, category='warning') ->
  clear_notifications()
  return if not message

  ($ '#notifications').append """
      <div class="alert alert-dismissable alert-#{category}">
        <button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>
        #{message}
      </div>
    """
