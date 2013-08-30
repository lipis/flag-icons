gae-init
========

**gae-init** is the easiest way to start new applications on Google App Engine
using Flask, Bootstrap and tons of other cool features.


Demo Page
---------

The latest version is always accessible from:
[http://gae-init.appspot.com](http://gae-init.appspot.com)

Documentation
-------------

Visit the [docs][] page for more information, where you can
also find a detailed [tutorial][] on how to build a phonebook application.

Running the Development Environment
-----------------------------------

    $ cd /path/to/project-name/main
    $ ./run.py -s

To test it visit `http://localhost:8080/` in your browser.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

To watch for changes of your `*.less` & `*.coffee` files and compile them
automatically to `*.css` & `*.js` run in another bash:

    $ ./run.py -w

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

For a complete list of commands:

    $ ./run -h

Deploying on Google App Engine
------------------------------

Before deploying make sure that the `app.yaml` and `config.py` are up to date
and you ran the `run.py` script to minify all the static files:

    $ ./run.py -m
    $ appcfg.py update .

Tech Stack
----------

  - [Google App Engine][]
  - [Python 2.7][]
  - [NDB][]
  - [Jinja2][]
  - [Flask][]
  - [jQuery][]
  - [CoffeeScript][]
  - [LessCSS][]
  - [Bootstrap][]
  - [Font Awesome][]
  - [NProgress][]

Requirements
------------

  - [Google App Engine SDK for Python][]
  - [node.js][]
  - [OSX][] or [Linux][] or [Windows][]

Contributions and Ideas
-----------------------

  - [tzador][]
  - [chris][]
  - [ksymeon][]
  - [gmist][]
  - [stefanlindmark][]
  - [joernhees][]

Author
------

[![Lipis flair on stackoverflow.com][lipisflair]][lipis]

[bootstrap]: http://getbootstrap.com/
[chris]: http://stackoverflow.com/users/226394/chris-top
[coffeescript]: http://coffeescript.org/
[docs]: http://docs.gae-init.appspot.com
[flask]: http://flask.pocoo.org/
[font awesome]: http://fortawesome.github.com/font-awesome/
[gmist]: https://github.com/gmist
[google app engine sdk for python]: https://developers.google.com/appengine/downloads
[google app engine]: https://developers.google.com/appengine/
[jinja2]: http://jinja.pocoo.org/docs/
[joernhees]: https://github.com/joernhees
[jquery]: http://jquery.com/
[ksymeon]: https://plus.google.com/102598378133436784997
[lesscss]: http://lesscss.org/
[linux]: http://www.ubuntu.com
[lipis]: http://stackoverflow.com/users/8418/lipis
[lipisflair]: http://stackexchange.com/users/flair/5282.png
[ndb]: https://developers.google.com/appengine/docs/python/ndb/
[node.js]: http://nodejs.org/
[nprogress]: http://ricostacruz.com/nprogress/
[osx]: http://www.apple.com/osx/
[python 2.7]: https://developers.google.com/appengine/docs/python/python27/using27
[stefanlindmark]: http://www.linkedin.com/in/stefanlindmark
[tutorial]: http://docs.gae-init.appspot.com/tutorial/
[tzador]: http://stackoverflow.com/users/165697/tzador
[windows]: http://windows.microsoft.com/
