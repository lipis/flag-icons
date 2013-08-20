gae-init
========

**gae-init** is the easiest way to start new applications on Google App Engine
using Flask, Bootstrap and tons of other cool features.


Demo Page
---------

The latest version is always accessible from: [http://gae-init.appspot.com][gaeinit]

Documentation
-------------

Visit the [docs][] page for more information, where you can
also find a detailed [tutorial][] on how to build a phonebook application.

Running the Development Environment
-----------------------------------

    $ cd /path/to/project-name/main
    $ ./run.py -cs

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

  - [Google App Engine][gae]
  - [Python 2.7][gaepython]
  - [NDB][]
  - [Jinja2][]
  - [Flask][]
  - [jQuery][]
  - [CoffeeScript][]
  - [LessCSS][]
  - [Bootstrap][]
  - [Font Awesome][fontawesome]

Requirements
------------

  - [Google App Engine SDK for Python][gaesdk]
  - [node.js][nodejs]
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

[gaeinit]: http://gae-init.appspot.com
[docs]: http://docs.gae-init.appspot.com
[tutorial]: http://docs.gae-init.appspot.com/tutorial/
[gae]: https://developers.google.com/appengine/
[gaepython]: https://developers.google.com/appengine/docs/python/python27/using27
[ndb]: https://developers.google.com/appengine/docs/python/ndb/
[jinja2]: http://jinja.pocoo.org/docs/
[flask]: http://flask.pocoo.org/
[jquery]: http://jquery.com/
[coffeescript]: http://coffeescript.org/
[lesscss]: http://lesscss.org/
[bootstrap]: http://getbootstrap.com/
[fontawesome]: http://fortawesome.github.com/Font-Awesome/

[gaesdk]: https://developers.google.com/appengine/downloads
[nodejs]: http://nodejs.org/
[osx]: http://www.apple.com/osx/
[linux]: http://www.ubuntu.com
[windows]: http://windows.microsoft.com/

[tzador]: http://stackoverflow.com/users/165697/tzador
[chris]: http://stackoverflow.com/users/226394/chris-top
[ksymeon]: https://plus.google.com/102598378133436784997
[gmist]: https://github.com/gmist
[stefanlindmark]: http://www.linkedin.com/in/stefanlindmark
[joernhees]: https://github.com/joernhees

[lipisflair]: http://stackexchange.com/users/flair/5282.png
[lipis]: http://stackoverflow.com/users/8418/lipis
