## www.pubnub.com - PubNub Real-time push service in the cloud.
# coding=utf8

## PubNub Real-time Push APIs and Notifications Framework
## Copyright (c) 2010 Stephen Blum
## http://www.pubnub.com/

## -----------------------------------
## PubNub 3.0 Real-time Push Cloud API
## -----------------------------------

import time
import hashlib
import urllib2

try:
    import json
except ImportError:
    from django.utils import simplejson as json

from google.appengine.api import urlfetch

class Pubnub():
    def __init__(
        self,
        publish_key,
        subscribe_key,
        secret_key = False,
        ssl_on = False,
        origin = 'pubsub.pubnub.com'
    ) :
        """
        #**
        #* Pubnub
        #*
        #* Init the Pubnub Client API
        #*
        #* @param string publish_key required key to send messages.
        #* @param string subscribe_key required key to receive messages.
        #* @param string secret_key required key to sign messages.
        #* @param boolean ssl required for 2048 bit encrypted messages.
        #* @param string origin PUBNUB Server Origin.
        #**

        ## Initiat Class
        pubnub = Pubnub( 'PUBLISH-KEY', 'SUBSCRIBE-KEY', 'SECRET-KEY', False )

        """
        self.origin        = origin
        self.limit         = 1800
        self.publish_key   = publish_key
        self.subscribe_key = subscribe_key
        self.secret_key    = secret_key
        self.ssl           = ssl_on

        if self.ssl :
            self.origin = 'https://' + self.origin
        else :
            self.origin = 'http://'  + self.origin


    def publish( self, args ) :
        """
        #**
        #* Publish
        #*
        #* Send a message to a channel.
        #*
        #* @param array args with channel and message.
        #* @return array success information.
        #**

        ## Publish Example
        info = pubnub.publish({
            'channel' : 'hello_world',
            'message' : {
                'some_text' : 'Hello my World'
            }
        })
        print(info)

        """
        ## Fail if bad input.
        if not (args['channel'] and args['message']) :
            print('Missing Channel or Message')
            return False

        ## Capture User Input
        channel = args['channel']
        message = json.dumps(args['message'])

        ## Sign Message
        if self.secret_key :
            signature = hashlib.md5('/'.join([
                self.publish_key,
                self.subscribe_key,
                self.secret_key,
                channel,
                message
            ])).hexdigest()
        else :
            signature = '0'

        ## Fail if message too long.
        if len(message) > self.limit :
            print('Message TOO LONG (' + str(self.limit) + ' LIMIT)')
            return [ 0, 'Message Too Long.' ]

        ## Send Message
        return self._request([
            'publish',
            self.publish_key,
            self.subscribe_key,
            signature,
            channel,
            '0',
            message
        ])


    def subscribe( self, args ) :
        """
        #**
        #* Subscribe
        #*
        #* This is BLOCKING.
        #* Listen for a message on a channel.
        #*
        #* @param array args with channel and message.
        #* @return false on fail, array on success.
        #**

        ## Subscribe Example
        def receive(message) :
            print(message)
            return True

        pubnub.subscribe({
            'channel'  : 'hello_world',
            'callback' : receive
        })

        """
        ## Fail if missing channel
        if not 'channel' in args :
            print('Missing Channel.')
            return False

        ## Fail if missing callback
        if not 'callback' in args :
            print('Missing Callback.')
            return False

        ## Capture User Input
        channel   = args['channel']
        callback  = args['callback']
        timetoken = 'timetoken' in args and args['timetoken'] or 0

        ## Begin Recusive Subscribe
        try :
            ## Wait for Message
            response = self._request([
                'subscribe',
                self.subscribe_key,
                channel,
                '0',
                str(timetoken)
            ])

            messages          = response[0]
            args['timetoken'] = response[1]

            ## If it was a timeout
            if not len(messages) :
                return self.subscribe(args)

            ## Run user Callback and Reconnect if user permits.
            for message in messages :
                if not callback(message) :
                    return

            ## Keep Listening.
            return self.subscribe(args)
        except :
            time.sleep(1)
            return self.subscribe(args)

        return True

    def history( self, args ) :
        """
        #**
        #* History
        #*
        #* Load history from a channel.
        #*
        #* @param array args with 'channel' and 'limit'.
        #* @return mixed false on fail, array on success.
        #*

        ## History Example
        history = pubnub.history({
            'channel' : 'hello_world',
            'limit'   : 1
        })
        print(history)

        """
        ## Capture User Input
        limit   = args.has_key('limit') and int(args['limit']) or 10
        channel = args['channel']

        ## Fail if bad input.
        if not channel :
            print('Missing Channel')
            return False

        ## Get History
        return self._request([
            'history',
            self.subscribe_key,
            channel,
            '0',
            str(limit)
        ]);

        """
        #**
        #* Time
        #*
        #* Timestamp from PubNub Cloud.
        #*
        #* @return int timestamp.
        #*

        ## PubNub Server Time Example
        timestamp = pubnub.time()
        print(timestamp)

        """
    def time(self) :
        return self._request([
            'time',
            '0'
        ])[0]

    def _request( self, request ) :
        ## Build URL
        url = self.origin + '/' + "/".join([
            "".join([ ' ~`!@#$%^&*()+=[]\\{}|;\':",./<>?'.find(ch) > -1 and
                hex(ord(ch)).replace( '0x', '%' ).upper() or
                ch for ch in list(bit)
            ]) for bit in request])

        ## Send Request Expecting JSONP Response
        response = urlfetch.fetch(url)

        return json.loads( response.content )

