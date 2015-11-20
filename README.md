gae-init-babel
==============
[![Slack Status](https://gae-init-slack.herokuapp.com/badge.svg)](https://gae-init-slack.herokuapp.com)

**gae-init-babel** is the easiest way to kick start new applications on Google
App Engine using Flask, Bootstrap, Babel and tons of other cool features.

Read more in the [docs][], where you can find a complete [feature list][],
a detailed [tutorial][] on how to build a phonebook application and more..

The latest version is always accessible from
[http://babel.gae-init.appspot.com](http://babel.gae-init.appspot.com)

Running the Development Environment
-----------------------------------

    $ cd /path/to/project-name
    $ gulp

To test it visit `http://localhost:8080/` in your browser.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

For a complete list of commands:

    $ gulp help


Initializing or Resetting the project
------------------------------------

    $ cd /path/to/project-name
    $ npm install
    $ gulp

If something goes wrong you can always do:

    $ gulp reset
    $ npm install
    $ gulp

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

To install [Gulp][] as a global package:

    $ npm install -g gulp

Deploying on Google App Engine
------------------------------

    $ gulp deploy

Before deploying make sure that the `main/app.yaml` and `gulp/config.coffee`
are up to date.

Tech Stack
----------

  - [Google App Engine][], [NDB][]
  - [Jinja2][], [Flask][], [Flask-RESTful][], [Flask-WTF][]
  - [CoffeeScript][], [Less][]
  - [Bootstrap][], [Font Awesome][], [Social Buttons][]
  - [jQuery][], [NProgress][], [Moment.js][]
  - [OpenID][] sign in (Google, Facebook, Twitter)
  - [Python 2.7][], [pip][], [virtualenv][]
  - [Gulp][], [Bower][]
  - [Babel][]

Requirements
------------

  - Being familiar with [gae-init][]

Support
-------

Due to lack of documentation if you run into any troubles, feel free to add an
issue and I'll be happy to improve or provide more info.

Author
------

[![Lipis flair on stackoverflow.com][lipisflair]][lipis]

[babel]: http://babel.edgewall.org/wiki/Download
[bootstrap]: http://getbootstrap.com/
[bower]: http://bower.io/
[coffeescript]: http://coffeescript.org/
[docs]: http://docs.gae-init.appspot.com
[feature list]: http://docs.gae-init.appspot.com/features/
[flask-restful]: https://flask-restful.readthedocs.org
[flask-wtf]: https://flask-wtf.readthedocs.org
[flask]: http://flask.pocoo.org/
[font awesome]: http://fortawesome.github.com/Font-Awesome/
[gae-init]: http://gae-init.appspot.com
[google app engine]: https://developers.google.com/appengine/
[gulp]: http://gulpjs.com
[jinja2]: http://jinja.pocoo.org/docs/
[jquery]: http://jquery.com/
[less]: http://lesscss.org/
[lipis]: http://stackoverflow.com/users/8418/lipis
[lipisflair]: http://stackexchange.com/users/flair/5282.png
[moment.js]: http://momentjs.com/
[ndb]: https://developers.google.com/appengine/docs/python/ndb/
[nprogress]: http://ricostacruz.com/nprogress/
[openid]: http://en.wikipedia.org/wiki/OpenID
[pip]: http://www.pip-installer.org/
[python 2.7]: https://developers.google.com/appengine/docs/python/python27/using27
[social buttons]: http://lipis.github.io/bootstrap-social/
[tutorial]: http://docs.gae-init.appspot.com/tutorial/
[virtualenv]: http://www.virtualenv.org/
[xcash]: https://github.com/xcash
