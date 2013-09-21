gae-init-babel
==============

**gae-init-babel** is the easiest way to start new applications on Google App Engine
using Flask, Bootstrap, Babel and tons of other cool features.


Demo Page
---------

The latest version is always accessible from:
[http://babel.gae-init.appspot.com](http://babel.gae-init.appspot.com)

Documentation
-------------

Visit the [docs][] page for more information, where you can
also find a detailed [tutorial][] on how to build a phonebook application.

Running the Development Environment
-----------------------------------

    $ cd /path/to/project-name
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
  - [Moment.js][]
  - [Babel][]

Requirements
------------

  - Being familiar with [gae-init][]
  - [Babel][] - `easy_install Babel`
  - [Jinja2][] - `easy_install Jinja2`

Support
-------

Due to lack of documentation if you run into any troubles, feel free to add an
issue and I'll be happy to improve or provide more info.

Author
------

[![Lipis flair on stackoverflow.com][lipisflair]][lipis]

[babel]: http://babel.edgewall.org/wiki/Download
[bootstrap]: http://getbootstrap.com/
[coffeescript]: http://coffeescript.org/
[docs]: http://docs.gae-init.appspot.com
[flask]: http://flask.pocoo.org/
[font awesome]: http://fortawesome.github.com/Font-Awesome/
[gae-init]: http://gae-init.appspot.com
[google app engine sdk for python]: https://developers.google.com/appengine/downloads
[google app engine]: https://developers.google.com/appengine/
[jinja2]: http://jinja.pocoo.org
[jquery]: http://jquery.com/
[lesscss]: http://lesscss.org/
[lipis]: http://stackoverflow.com/users/8418/lipis
[lipisflair]: http://stackexchange.com/users/flair/5282.png
[moment.js]: http://momentjs.com/
[ndb]: https://developers.google.com/appengine/docs/python/ndb/
[node.js]: http://nodejs.org/
[nprogress]: http://ricostacruz.com/nprogress/
[osx]: http://www.apple.com/osx/
[python 2.7]: https://developers.google.com/appengine/docs/python/python27/using27
[tutorial]: http://docs.gae-init.appspot.com/tutorial/
