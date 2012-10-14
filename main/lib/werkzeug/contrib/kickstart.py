# -*- coding: utf-8 -*-
"""
    werkzeug.contrib.kickstart
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module provides some simple shortcuts to make using Werkzeug simpler
    for small scripts.

    These improvements include predefined `Request` and `Response` objects as
    well as a predefined `Application` object which can be customized in child
    classes, of course.  The `Request` and `Reponse` objects handle URL
    generation as well as sessions via `werkzeug.contrib.sessions` and are
    purely optional.

    There is also some integration of template engines.  The template loaders
    are, of course, not neccessary to use the template engines in Werkzeug,
    but they provide a common interface.  Currently supported template engines
    include Werkzeug's minitmpl and Genshi_.  Support for other engines can be
    added in a trivial way.  These loaders provide a template interface
    similar to the one used by Django_.

    .. _Genshi: http://genshi.edgewall.org/
    .. _Django: http://www.djangoproject.com/

    :copyright: (c) 2011 by the Werkzeug Team, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""
from os import path
from werkzeug.wrappers import Request as RequestBase, Response as ResponseBase
from werkzeug.templates import Template
from werkzeug.exceptions import HTTPException
from werkzeug.routing import RequestRedirect

__all__ = ['Request', 'Response', 'TemplateNotFound', 'TemplateLoader',
           'GenshiTemplateLoader', 'Application']

from warnings import warn
warn(DeprecationWarning('werkzeug.contrib.kickstart is deprecated and '
                        'will be removed in Werkzeug 1.0'))


class Request(RequestBase):
    """A handy subclass of the base request that adds a URL builder.
    It when supplied a session store, it is also able to handle sessions.
    """

    def __init__(self, environ, url_map,
            session_store=None, cookie_name=None):
        # call the parent for initialization
        RequestBase.__init__(self, environ)
        # create an adapter
        self.url_adapter = url_map.bind_to_environ(environ)
        # create all stuff for sessions
        self.session_store = session_store
        self.cookie_name = cookie_name

        if session_store is not None and cookie_name is not None:
            if cookie_name in self.cookies:
                # get the session out of the storage
                self.session = session_store.get(self.cookies[cookie_name])
            else:
                # create a new session
                self.session = session_store.new()

    def url_for(self, callback, **values):
        return self.url_adapter.build(callback, values)


class Response(ResponseBase):
    """
    A subclass of base response which sets the default mimetype to text/html.
    It the `Request` that came in is using Werkzeug sessions, this class
    takes care of saving that session.
    """
    default_mimetype = 'text/html'

    def __call__(self, environ, start_response):
        # get the request object
        request = environ['werkzeug.request']

        if request.session_store is not None:
            # save the session if neccessary
            request.session_store.save_if_modified(request.session)

            # set the cookie for the browser if it is not there:
            if request.cookie_name not in request.cookies:
                self.set_cookie(request.cookie_name, request.session.sid)

        # go on with normal response business
        return ResponseBase.__call__(self, environ, start_response)


class Processor(object):
    """A request and response processor - it is what Django calls a
    middleware, but Werkzeug also includes straight-foward support for real
    WSGI middlewares, so another name was chosen.

    The code of this processor is derived from the example in the Werkzeug
    trac, called `Request and Response Processor
    <http://dev.pocoo.org/projects/werkzeug/wiki/RequestResponseProcessor>`_
    """

    def process_request(self, request):
        return request

    def process_response(self, request, response):
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        """process_view() is called just before the Application calls the
        function specified by view_func.

        If this returns None, the Application processes the next Processor,
        and if it returns something else (like a Response instance), that
        will be returned without any further processing.
        """
        return None

    def process_exception(self, request, exception):
        return None


class Application(object):
    """A generic WSGI application which can be used to start with Werkzeug in
    an easy, straightforward way.
    """

    def __init__(self, name, url_map, session=False, processors=None):
        # save the name and the URL-map, as it'll be needed later on
        self.name = name
        self.url_map = url_map
        # save the list of processors if supplied
        self.processors = processors or []
        # create an instance of the storage
        if session:
            self.store = session
        else:
            self.store = None

    def __call__(self, environ, start_response):
        # create a request - with or without session support
        if self.store is not None:
            request = Request(environ, self.url_map,
                session_store=self.store, cookie_name='%s_sid' % self.name)
        else:
            request = Request(environ, self.url_map)

        # apply the request processors
        for processor in self.processors:
            request = processor.process_request(request)

        try:
            # find the callback to which the URL is mapped
            callback, args = request.url_adapter.match(request.path)
        except (HTTPException, RequestRedirect), e:
            response = e
        else:
            # check all view processors
            for processor in self.processors:
                action = processor.process_view(request, callback, (), args)
                if action is not None:
                    # it is overriding the default behaviour, this is
                    # short-circuiting the processing, so it returns here
                    return action(environ, start_response)

            try:
                response = callback(request, **args)
            except Exception, exception:
                # the callback raised some exception, need to process that
                for processor in reversed(self.processors):
                    # filter it through the exception processor
                    action = processor.process_exception(request, exception)
                    if action is not None:
                        # the exception processor returned some action
                        return action(environ, start_response)
                # still not handled by a exception processor, so re-raise
                raise

        # apply the response processors
        for processor in reversed(self.processors):
            response = processor.process_response(request, response)

        # return the completely processed response
        return response(environ, start_response)


    def config_session(self, store, expiration='session'):
        """
        Configures the setting for cookies. You can also disable cookies by
        setting store to None.
        """
        self.store = store
        # expiration=session is the default anyway
        # TODO: add settings to define the expiration date, the domain, the
        # path any maybe the secure parameter.


class TemplateNotFound(IOError, LookupError):
    """
    A template was not found by the template loader.
    """

    def __init__(self, name):
        IOError.__init__(self, name)
        self.name = name


class TemplateLoader(object):
    """
    A simple loader interface for the werkzeug minitmpl
    template language.
    """

    def __init__(self, search_path, encoding='utf-8'):
        self.search_path = path.abspath(search_path)
        self.encoding = encoding

    def get_template(self, name):
        """Get a template from a given name."""
        filename = path.join(self.search_path, *[p for p in name.split('/')
                                                 if p and p[0] != '.'])
        if not path.exists(filename):
            raise TemplateNotFound(name)
        return Template.from_file(filename, self.encoding)

    def render_to_response(self, *args, **kwargs):
        """Load and render a template into a response object."""
        return Response(self.render_to_string(*args, **kwargs))

    def render_to_string(self, *args, **kwargs):
        """Load and render a template into a unicode string."""
        try:
            template_name, args = args[0], args[1:]
        except IndexError:
            raise TypeError('name of template required')
        return self.get_template(template_name).render(*args, **kwargs)


class GenshiTemplateLoader(TemplateLoader):
    """A unified interface for loading Genshi templates. Actually a quite thin
    wrapper for Genshi's TemplateLoader.

    It sets some defaults that differ from the Genshi loader, most notably
    auto_reload is active. All imporant options can be passed through to
    Genshi.
    The default output type is 'html', but can be adjusted easily by changing
    the `output_type` attribute.
    """
    def __init__(self, search_path, encoding='utf-8', **kwargs):
        TemplateLoader.__init__(self, search_path, encoding)
        # import Genshi here, because we don't want a general Genshi
        # dependency, only a local one
        from genshi.template import TemplateLoader as GenshiLoader
        from genshi.template.loader import TemplateNotFound

        self.not_found_exception = TemplateNotFound
        # set auto_reload to True per default
        reload_template = kwargs.pop('auto_reload', True)
        # get rid of default_encoding as this template loaders overwrites it
        # with the value of encoding
        kwargs.pop('default_encoding', None)

        # now, all arguments are clean, pass them on
        self.loader = GenshiLoader(search_path, default_encoding=encoding,
                auto_reload=reload_template, **kwargs)

        # the default output is HTML but can be overridden easily
        self.output_type = 'html'
        self.encoding = encoding

    def get_template(self, template_name):
        """Get the template which is at the given name"""
        try:
            return self.loader.load(template_name, encoding=self.encoding)
        except self.not_found_exception, e:
            # catch the exception raised by Genshi, convert it into a werkzeug
            # exception (for the sake of consistency)
            raise TemplateNotFound(template_name)

    def render_to_string(self, template_name, context=None):
        """Load and render a template into an unicode string"""
        # create an empty context if no context was specified
        context = context or {}
        tmpl = self.get_template(template_name)
        # render the template into a unicode string (None means unicode)
        return tmpl. \
            generate(**context). \
            render(self.output_type, encoding=None)
