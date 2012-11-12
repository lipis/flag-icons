window.subscribe_chat = () ->
  channel = $('html').data('channel-name')
  subscribe_channel(channel, on_chat_message_received)
  channel_history(channel, 8, on_chat_history)

  $('.chat-message').select()

  $('body').on 'click', '.chat-send', ->
    send_chat_message()

  $('body').on 'keydown', '.chat-message', (event) ->
    if event.keyCode == 13
      send_chat_message()

send_chat_message = () ->
  channel = $('html').data('channel-name')
  message = $('.chat-message').val()
  $('.chat-message').val('')
  if message
    channel_send channel,
      'name': $('.chat-message').data('name')
      'message': message
      'time': new Date().getTime()

window.on_chat_message_received = (message) ->
  time = new Date(message.time)
  datestamp = "#{time.getFullYear()}-#{leading_zero(time.getMonth())}-#{leading_zero(time.getDate())}"
  timestamp = "#{leading_zero(time.getHours())}:#{leading_zero(time.getMinutes())}:#{leading_zero(time.getSeconds())}"
  $('.chat-log').prepend """
    <hr>
    <h4>#{message.name} <small>#{datestamp} @ #{timestamp}</small></h4>
    <h5>#{message.message}</h5>
  """

window.on_chat_history = (messages) ->
  for message in messages
    on_chat_message_received(message)

leading_zero = (number) ->
  if number < 10
    return '0' + number
  return number
