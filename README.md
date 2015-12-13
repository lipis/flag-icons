gae-init
========

[![Slack Status](https://gae-init-slack.herokuapp.com/badge.svg)](https://gae-init-slack.herokuapp.com)

> **gae-init** is the easiest boilerplate to kick start new applications on Google
App Engine using Flask, RESTful, Bootstrap and tons of other cool features.

Read the [documentation][], where you can find a complete [feature list][],
a detailed [tutorial][], the [how to][] section and more..

The latest version is always accessible from
[https://gae-init.appspot.com](https://gae-init.appspot.com)

Running the Development Environment
-----------------------------------

```bash
$ cd /path/to/project-name
$ gulp
```

To test it visit `http://localhost:8080/` in your browser.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

For a complete list of commands:

```bash
$ gulp help
```

Initializing or Resetting the project
------------------------------------

```bash
$ cd /path/to/project-name
$ npm install
$ gulp
```

If something goes wrong you can always do:

```bash
$ gulp reset
$ npm install
$ gulp
```

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

To install [Gulp][] as a global package:

```bash
$ npm install -g gulp
```

Deploying on Google App Engine
------------------------------

```bash
$ gulp deploy
```

Before deploying make sure that the `main/app.yaml` and `gulp/config.coffee`
are up to date.

Tech Stack
----------

  - [Google App Engine][], [NDB][]
  - [Jinja2][], [Flask][], [Flask-RESTful][], [Flask-WTF][]
  - [CoffeeScript][], [Less][]
  - [Bootstrap][], [Font Awesome][], [Social Buttons][]
  - [jQuery][], [Moment.js][]
  - [OpenID][] sign in (Google, Facebook, Twitter and more)
  - [Python 2.7][], [pip][], [virtualenv][]
  - [Gulp][], [Bower][]

Requirements
------------

  - [Google App Engine SDK for Python][]
  - [Node.js][], [pip][], [virtualenv][]
  - [OS X][] or [Linux][] or [Windows][]

Make sure you have all of the above or refer to the docs on how to
[install the requirements](http://docs.gae-init.appspot.com/requirement/).

Contributions and Ideas
-----------------------

  - [gmist][]
  - [mdxs][]
  - [joernhees][]
  - [chris][]
  - [tzador][]
  - [stefanlindmark][]
  - [ksymeon][]
  - [many more..][]

Author
------

[![Lipis flair on stackoverflow.com][lipisflair]][lipis]

[bootstrap]: http://getbootstrap.com/
[bower]: http://bower.io/
[chris]: http://stackoverflow.com/users/226394/chris-top
[coffeescript]: http://coffeescript.org/
[documentation]: http://docs.gae-init.appspot.com
[feature list]: http://docs.gae-init.appspot.com/features/
[flask-restful]: https://flask-restful.readthedocs.org
[flask-wtf]: https://flask-wtf.readthedocs.org
[flask]: http://flask.pocoo.org/
[font awesome]: http://fortawesome.github.com/Font-Awesome/
[gmist]: https://github.com/gmist
[google app engine sdk for python]: https://developers.google.com/appengine/downloads
[google app engine]: https://developers.google.com/appengine/
[gulp]: http://gulpjs.com
[how to]: http://docs.gae-init.appspot.com/howto/
[jinja2]: http://jinja.pocoo.org/docs/
[joernhees]: https://github.com/joernhees
[jquery]: https://jquery.com/
[ksymeon]: https://plus.google.com/+KostasSymeonidis
[less]: http://lesscss.org/
[lesscss]: http://lesscss.org/
[linux]: http://www.ubuntu.com
[lipis]: http://stackoverflow.com/users/8418/lipis
[lipisflair]: http://stackexchange.com/users/flair/5282.png
[many more..]: https://github.com/gae-init/gae-init/graphs/contributors
[mdxs]: https://github.com/mdxs
[moment.js]: http://momentjs.com/
[ndb]: https://developers.google.com/appengine/docs/python/ndb/
[node.js]: http://nodejs.org/
[openid]: http://en.wikipedia.org/wiki/OpenID
[os x]: http://www.apple.com/osx/
[pip]: http://www.pip-installer.org/
[python 2.7]: https://developers.google.com/appengine/docs/python/python27/using27
[social buttons]: http://lipis.github.io/bootstrap-social/
[stefanlindmark]: http://www.linkedin.com/in/stefanlindmark
[tutorial]: http://docs.gae-init.appspot.com/tutorial/
[tzador]: https://plus.google.com/+TimZadorozhny
[virtualenv]: http://www.virtualenv.org/
[windows]: http://windows.microsoft.com/
