gae-init
========

**gae-init** is the easiest way to kick start new applications on Google
App Engine using Flask, Bootstrap and tons of other cool features.

Read more in the [docs][], where you can find a complete [feature list][],
a detailed [tutorial][] on how to build a phonebook application and more..

The latest version is always accessible from
[http://gae-init.appspot.com](http://gae-init.appspot.com)

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

Requirements
------------

  - [Google App Engine SDK for Python][]
  - [Node.js][], [pip][], [virtualenv][]
  - [OSX][] or [Linux][] or [Windows][]

Contributions and Ideas
-----------------------

  - [tzador][]
  - [chris][]
  - [ksymeon][]
  - [gmist][]
  - [stefanlindmark][]
  - [joernhees][]
  - [xcash][]
  - [mdxs][]

Author
------

[![Lipis flair on stackoverflow.com][lipisflair]][lipis]

[bootstrap]: http://getbootstrap.com/
[bower]: http://bower.io/
[chris]: http://stackoverflow.com/users/226394/chris-top
[coffeescript]: http://coffeescript.org/
[docs]: http://docs.gae-init.appspot.com
[feature list]: http://docs.gae-init.appspot.com/features/
[flask-restful]: https://flask-restful.readthedocs.org
[flask-wtf]: https://flask-wtf.readthedocs.org
[flask]: http://flask.pocoo.org/
[font awesome]: http://fortawesome.github.com/Font-Awesome/
[gmist]: https://github.com/gmist
[google app engine sdk for python]: https://developers.google.com/appengine/downloads
[google app engine]: https://developers.google.com/appengine/
[gulp]: http://gulpjs.com
[jinja2]: http://jinja.pocoo.org/docs/
[joernhees]: https://github.com/joernhees
[jquery]: http://jquery.com/
[ksymeon]: https://plus.google.com/102598378133436784997
[less]: http://lesscss.org/
[lesscss]: http://lesscss.org/
[linux]: http://www.ubuntu.com
[lipis]: http://stackoverflow.com/users/8418/lipis
[lipisflair]: http://stackexchange.com/users/flair/5282.png
[mdxs]: https://github.com/mdxs
[moment.js]: http://momentjs.com/
[ndb]: https://developers.google.com/appengine/docs/python/ndb/
[node.js]: http://nodejs.org/
[nprogress]: http://ricostacruz.com/nprogress/
[openid]: http://en.wikipedia.org/wiki/OpenID
[osx]: http://www.apple.com/osx/
[pip]: http://www.pip-installer.org/
[python 2.7]: https://developers.google.com/appengine/docs/python/python27/using27
[social buttons]: http://lipis.github.io/bootstrap-social/
[stefanlindmark]: http://www.linkedin.com/in/stefanlindmark
[tutorial]: http://docs.gae-init.appspot.com/tutorial/
[tzador]: http://stackoverflow.com/users/165697/tzador
[virtualenv]: http://www.virtualenv.org/
[windows]: http://windows.microsoft.com/
[xcash]: https://github.com/xcash
