window.channel_get = () ->
  if window.PUBNUB_PUBLISH and window.PUBNUB_SUBSCRIBE
    return PUBNUB
      publish_key   : window.PUBNUB_PUBLISH
      subscribe_key : window.PUBNUB_SUBSCRIBE
      ssl           : false
      origin        : 'pubsub.pubnub.com'
  return null

window.subscribe_channel = (channel, callback) ->
  pubnub = channel_get()
  if pubnub
    pubnub.subscribe
        channel: channel
        connect: null
        callback: callback or null
    return true
  return false

window.channel_send = (channel, message, callback) ->
  pubnub = channel_get()
  if pubnub
    pubnub.publish
      channel: channel
      message: message
      callback : callback or null
    return true
  return false

window.channel_history = (channel, limit, callback) ->
  pubnub = channel_get()
  if pubnub
    pubnub.history({channel: channel, limit: limit}, callback or null)
