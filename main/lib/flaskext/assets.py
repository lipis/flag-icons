from __future__ import with_statement
from os import path
from flask import _request_ctx_stack, url_for
from webassets import Bundle
from webassets.env import BaseEnvironment, ConfigStorage


__version__ = (0, 6, 2)

__all__ = ('Environment', 'Bundle',)


class FlaskConfigStorage(ConfigStorage):
    """Uses the config object of a Flask app as the backend: either the app
    instance bound to the extension directly, or the current Flasp app on
    the stack.

    Also provides per-application defaults for some values.

    Note that if no app is available, this config object is basically
    unusable - this is by design; this could also let the user set defaults
    by writing to a container not related to any app, which would be used
    as a fallback if a current app does not include a key. However, at least
    for now, I specifically made the choice to keep things simple and not
    allow global across-app defaults.
    """

    _mapping = [
        'debug', 'cache', 'updater', 'auto_create', 'expire', 'directory', 'url',]

    def __init__(self, *a, **kw):
        self._defaults = {}
        ConfigStorage.__init__(self, *a, **kw)

    def _transform_key(self, key):
        if key.lower() in self._mapping:
            return "ASSETS_%s" % key.upper()
        else:
            return key.upper()

    def setdefault(self, key, value):
        """We may not always be connected to an app, but we still need
        to provide a way to the base environment to set it's defaults.
        """
        try:
            super(FlaskConfigStorage, self).setdefault(key, value)
        except RuntimeError:
            self._defaults.__setitem__(key, value)

    def __contains__(self, key):
        return self._transform_key(key) in self.env._app.config

    def __getitem__(self, key):
        # First try the current app's config
        public_key = self._transform_key(key)
        if self.env._app:
            if public_key in self.env._app.config:
                return self.env._app.config[public_key]

        # Try a non-app specific default value
        if key in self._defaults:
            return self._defaults.__getitem__(key)

        # Finally try to use a default based on the current app
        deffunc = getattr(self, "_app_default_%s" % key, False)
        if deffunc:
            return deffunc()

        # We've run out of options
        raise KeyError()

    def __setitem__(self, key, value):
        self.env._app.config[self._transform_key(key)] = value

    def __delitem__(self, key):
        del self.env._app.config[self._transform_key(key)]



def get_static_folder(app_or_blueprint):
    """Return the static folder of the given Flask app
    instance, or module/blueprint.

    In newer Flask versions this can be customized, in older
    ones (<=0.6) the folder is fixed.
    """
    if hasattr(app_or_blueprint, 'static_folder'):
        return app_or_blueprint.static_folder
    return path.join(app_or_blueprint.root_path, 'static')


class Environment(BaseEnvironment):

    config_storage_class = FlaskConfigStorage

    def __init__(self, app=None):
        self.app = app
        super(Environment, self).__init__()
        if app:
            self.init_app(app)

    @property
    def _app(self):
        """The application object to work with; this is either the app
        that we have been bound to, or the current application.
        """
        if self.app is not None:
            return self.app
        else:
            ctx = _request_ctx_stack.top
            if ctx is not None:
                return ctx.app
        raise RuntimeError('assets instance not bound to an application, '+
                            'and no application in current context')

    def absurl(self, fragment):
        if self.config.get('url') is not None:
            # If a manual base url is configured, skip any
            # blueprint-based auto-generation.
            return super(Environment, self).absurl(fragment)
        else:
            try:
                filename, query = fragment.split('?', 1)
                query = '?' + query
            except (ValueError):
                filename = fragment
                query = ''

            if hasattr(self._app, 'blueprints'):
                try:
                    blueprint, name = filename.split('/', 1)
                    self._app.blueprints[blueprint] # generates keyerror if no module
                    endpoint = '%s.static' % blueprint
                    filename = name
                except (ValueError, KeyError):
                    endpoint = 'static'
            else:
                # Module support for Flask < 0.7
                try:
                    module, name = filename.split('/', 1)
                    self._app.modules[module] # generates keyerror if no module
                    endpoint = '%s.static' % module
                    filename = name
                except (ValueError, KeyError):
                    endpoint = '.static'

            ctx = None
            if not _request_ctx_stack.top:
                ctx = self._app.test_request_context()
                ctx.push()
            try:
                return url_for(endpoint, filename=filename) + query
            finally:
                if ctx:
                    ctx.pop()

    def abspath(self, path):
        """Still needed to resolve the output path.
        XXX: webassets needs to call _normalize_source_path
        for this!
        """
        return self._normalize_source_path(path)

    # XXX: This is required because in a couple of places, webassets 0.6
    # still access env.directory, at one point even directly. We need to
    # fix this for 0.6 compatibility, but it might be preferrable to
    # introduce another API similar to _normalize_source_path() for things
    # like the cache directory and output files.
    def set_directory(self, directory):
        self.config['directory'] = directory
    def get_directory(self):
        if self.config.get('directory') is not None:
            return self.config['directory']
        return get_static_folder(self._app)
    directory = property(get_directory, set_directory, doc=
    """The base directory to which all paths will be relative to.
    """)

    def _normalize_source_path(self, filename):
        if path.isabs(filename):
            return filename
        if self.config.get('directory') is not None:
            return super(Environment, self).abspath(filename)
        try:
            if hasattr(self._app, 'blueprints'):
                blueprint, name = filename.split('/', 1)
                directory = get_static_folder(self._app.blueprints[blueprint])
                filename = name
            else:
                # Module support for Flask < 0.7
                module, name = filename.split('/', 1)
                directory = get_static_folder(self._app.modules[module])
                filename = name
        except (ValueError, KeyError):
            directory = get_static_folder(self._app)
        return path.abspath(path.join(directory, filename))

    def init_app(self, app):
        app.jinja_env.add_extension('webassets.ext.jinja2.AssetsExtension')
        app.jinja_env.assets_environment = self


try:
    from flaskext import script
except ImportError:
    pass
else:
    import argparse

    class CatchAllParser(object):
        def parse_known_args(self, app_args):
            return argparse.Namespace(), app_args

    class ManageAssets(script.Command):
        """Manage assets."""
        capture_all_args = True

        def __init__(self, assets_env=None):
            self.env = assets_env

        def create_parser(self, prog):
            return CatchAllParser()

        def run(self, args):
            """Runs the management script.
            If ``self.env`` is not defined, it will import it from
            ``current_app``.
            """

            if not self.env:
                from flask import current_app
                self.env = current_app.jinja_env.assets_environment

            from webassets import script
            return script.main(args, env=self.env)

    __all__ = __all__ + ('ManageAssets',)
