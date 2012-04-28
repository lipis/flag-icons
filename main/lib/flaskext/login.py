# -*- coding: utf-8 -*-
"""
flaskext.login
==============

This module provides user session management for Flask. It lets you log your
users in and out in a database-independent manner.

:copyright: (C) 2011 by Matthew Frazier.
:license:   MIT/X11, see LICENSE for more details.
"""
import hmac
from datetime import datetime, timedelta
from flask import (current_app, session, _request_ctx_stack, redirect, url_for,
                   request, flash, abort)
from flask.signals import Namespace
from functools import wraps
from hashlib import sha1, md5
from urlparse import urlparse, urlunparse
from werkzeug.local import LocalProxy
from werkzeug.urls import url_decode, url_encode

_signals = Namespace()


def _get_user():
    return getattr(_request_ctx_stack.top, "user", None)


def _cookie_digest(payload, key=None):
    if key is None:
        key = current_app.config["SECRET_KEY"]
    payload = payload.encode("utf8")
    mac = hmac.new(key, payload, sha1)
    return mac.hexdigest()


def encode_cookie(payload):
    """
    This will encode a `unicode` value into a cookie, and sign that cookie
    with the app's secret key.
    
    :param payload: The value to encode, as `unicode`.
    """
    return u"%s|%s" % (payload, _cookie_digest(payload))


def decode_cookie(cookie):
    """
    This decodes a cookie given by `encode_cookie`. If verification of the
    cookie fails, `None` will be returned.
    
    :param cookie: An encoded cookie.
    """
    try:
        payload, digest = cookie.rsplit(u"|", 1)
        digest = digest.encode("ascii")
    except ValueError:
        return None
    if _cookie_digest(payload) == digest:
        return payload
    else:
        return None


def make_next_param(login, current):
    """
    Reduces the scheme and host from a given URL so it can be passed to
    the given `login` URL more efficiently.
    
    :param login: The login URL being redirected to.
    :param current: The URL to reduce.
    """
    login_scheme, login_netloc = urlparse(login)[:2]
    current_scheme, current_netloc = urlparse(current)[:2]
    if ((not login_scheme or login_scheme == current_scheme) and
        (not login_netloc or login_netloc == current_netloc)):
        parsed = urlparse(current)
        return urlunparse(("", "", parsed[2], parsed[3], parsed[4], ""))
    return current


def login_url(login_view, next_url=None, next_field="next"):
    """
    Creates a URL for redirecting to a login page. If only `login_view` is
    provided, this will just return the URL for it. If `next_url` is provided,
    however, this will append a ``next=URL`` parameter to the query string
    so that the login view can redirect back to that URL.
    
    :param login_view: The name of the login view. (Alternately, the actual
                       URL to the login view.)
    :param next_url: The URL to give the login view for redirection.
    :param next_field: What field to store the next URL in. (It defaults to
                       ``next``.)
    """
    if login_view.startswith(("https://", "http://", "/")):
        base = login_view
    else:
        base = url_for(login_view)
    if next_url is None:
        return base
    parts = list(urlparse(base))
    md = url_decode(parts[4])
    md[next_field] = make_next_param(base, next_url)
    parts[4] = url_encode(md, sort=True)
    return urlunparse(parts)


def make_secure_token(*args, **options):
    """
    This will create a secure token that you can use as an authentication
    token for your users. It uses heavy-duty HMAC encryption to prevent people
    from guessing the information. (To make it even more effective, if you
    will never need to regenerate the token, you can  pass some random data
    as one of the arguments.)
    
    :param args: The data to include in the token.
    :param options: To manually specify a secret key, pass ``key=THE_KEY``.
                    Otherwise, the current app's secret key will be used.
    """
    key = options.get("key")
    if key is None:
        key = current_app.config["SECRET_KEY"]
    payload = "\0".join((
        s.encode("utf8") if isinstance(s, unicode) else s) for s in args
    )
    mac = hmac.new(key, payload, sha1)
    return mac.hexdigest().decode("utf8")


def _create_identifier():
    base = unicode("%s|%s" % (request.remote_addr,
                              request.headers.get("User-Agent")), 'utf8')
    hsh = md5()
    hsh.update(base.encode("utf8"))
    return hsh.digest()


#: The default name of the "remember me" cookie (``remember_token``)
COOKIE_NAME = "remember_token"

#: The default time before the "remember me" cookie expires (365 days).
COOKIE_DURATION = timedelta(days=365)

#: The default flash message to display when users need to log in.
LOGIN_MESSAGE = u"Please log in to access this page."

#: The default flash message to display when users need to reauthenticate.
REFRESH_MESSAGE = u"Please reauthenticate to access this page."


class LoginManager(object):
    """
    This object is used to hold the settings used for logging in.
    Instances of `LoginManager` are *not* bound to specific apps, so
    you can create one in the main body of your code and then bind it to your
    app in a factory function.
    """
    def __init__(self):
        #: A class or factory function that produces an anonymous user, which
        #: is used when no one is logged in.
        self.anonymous_user = AnonymousUser
        #: The name of the view to redirect to when the user needs to log in.
        #: (This can be an absolute URL as well, if your authentication
        #: machinery is external to your application.)
        self.login_view = None
        #: The message to flash when a user is redirected to the login page.
        self.login_message = LOGIN_MESSAGE
        #: The name of the view to redirect to when the user needs to
        #: reauthenticate.
        self.refresh_view = None
        #: The message to flash when a user is redirected to the "needs
        #: refresh" page.
        self.needs_refresh_message = REFRESH_MESSAGE
        #: The mode to use session protection in. This can be either
        #: ``"basic"`` (the default) or ``"strong"``, or `None` to disable it.
        self.session_protection = "basic"
        self.token_callback = None
        self.user_callback = None
        self.unauthorized_callback = None
        self.needs_refresh_callback = None
    
    def user_loader(self, callback):
        """
        This sets the callback for reloading a user from the session. The
        function you set should take a user ID (a `unicode`) and return a
        user object, or `None` if the user does not exist.
        
        :param callback: The callback for retrieving a user object.
        """
        self.user_callback = callback
    
    def token_loader(self, callback):
        """
        This sets the callback for loading a user from an authentication
        token. The function you set should take an authentication token
        (a `unicode, as returned by a user's `get_auth_token` method) and
        return a user object, or `None` if the user does not exist.
        
        :param callback: The callback for retrieving a user object.
        """
        self.token_callback = callback
    
    def setup_app(self, app, add_context_processor=True):
        """
        Configures an application. This registers a `before_request` and an
        `after_request` call, and attaches this `LoginManager` to it as
        ``app.login_manager``.
        
        :param app: The `flask.Flask` object to configure.
        :param add_context_processor: Whether to add a context processor to
                                      the app that adds a `current_user`
                                      variable to the template.
        """
        app.login_manager = self
        app.before_request(self._load_user)
        app.after_request(self._update_remember_cookie)
        if add_context_processor:
            app.context_processor(_user_context_processor)
    
    def unauthorized_handler(self, callback):
        """
        This will set the callback for the `unauthorized` method, which among
        other things is used by `login_required`. It takes no arguments, and
        should return a response to be sent to the user instead of their
        normal view.
        
        :param callback: The callback for unauthorized users.
        """
        self.unauthorized_callback = callback
    
    def unauthorized(self):
        """
        This is called when the user is required to log in. If you register a
        callback with `unauthorized_handler`, then it will be called.
        Otherwise, it will take the following actions:
        
        - Flash `login_message` to the user.
        - Redirect the user to `login_view`. (The page they were attempting
          to access will be passed in the `next` query string variable, so
          you can redirect there if present instead of the homepage.)
        
        If `login_view` is not defined, then it will simply raise a 401
        (Unauthorized) error instead.
        
        This should be returned from a view or before/after_request function,
        otherwise the redirect will have no effect.
        """
        user_unauthorized.send(current_app._get_current_object())
        if self.unauthorized_callback:
            return self.unauthorized_callback()
        if not self.login_view:
            abort(401)
        flash(self.login_message)
        return redirect(login_url(self.login_view, request.url))
    
    def needs_refresh_handler(self, callback):
        """
        This will set the callback for the `needs_refresh` method, which among
        other things is used by `fresh_login_required`. It takes no arguments,
        and should return a response to be sent to the user instead of their
        normal view.
        
        :param callback: The callback for unauthorized users.
        """
        self.needs_refresh_callback = callback
    
    def needs_refresh(self):
        """
        This is called when the user is logged in, but they need to be
        reauthenticated because their session is stale. If you register a
        callback with `needs_refresh_handler`, then it will be called.
        Otherwise, it will take the following actions:
        
        - Flash `needs_refresh_message` to the user.
        - Redirect the user to `refresh_view`. (The page they were attempting
          to access will be passed in the `next` query string variable, so
          you can redirect there if present instead of the homepage.)
        
        If `refresh_view` is not defined, then it will simply raise a 403
        (Forbidden) error instead.
        
        This should be returned from a view or before/after_request function,
        otherwise the redirect will have no effect.
        """
        user_needs_refresh.send(current_app._get_current_object())
        if self.needs_refresh_callback:
            return self.needs_refresh_callback()
        if not self.refresh_view:
            abort(403)
        flash(self.needs_refresh_message)
        return redirect(login_url(self.refresh_view, request.url))
    
    def _load_user(self):
        config = current_app.config
        if config.get("SESSION_PROTECTION", self.session_protection):
            deleted = self._session_protection()
            if deleted:
                self.reload_user()
                return
        # If a remember cookie is set, and the session is not, move the
        # cookie user ID to the session.
        cookie_name = config.get("REMEMBER_COOKIE_NAME", COOKIE_NAME)
        if cookie_name in request.cookies and "user_id" not in session:
            self._load_from_cookie(request.cookies[cookie_name])
        else:
            self.reload_user()
    
    def _session_protection(self):
        sess = session._get_current_object()
        ident = _create_identifier()
        if "_id" not in sess:
            sess["_id"] = ident
        elif ident != sess["_id"]:
            app = current_app._get_current_object()
            mode = app.config.get("SESSION_PROTECTION",
                                  self.session_protection)
            if mode == "basic" or sess.permanent:
                sess["_fresh"] = False
                session_protected.send(app)
                return False
            elif mode == "strong":
                sess.clear()
                sess["remember"] = "clear"
                session_protected.send(app)
                return True
        return False
                
    
    def reload_user(self):
        ctx = _request_ctx_stack.top
        user_id = session.get("user_id", None)
        if user_id is None:
            ctx.user = self.anonymous_user()
        else:
            user = self.user_callback(user_id)
            if user is None:
                logout_user()
            else:
                ctx.user = user
    
    def _load_from_cookie(self, cookie):
        if self.token_callback:
            user = self.token_callback(cookie)
            if user is not None:
                session["user_id"] = user.get_id()
                session["_fresh"] = False
                _request_ctx_stack.top.user = user
            else:
                self.reload_user()
        else:
            user_id = decode_cookie(cookie)
            if user_id is not None:
                session["user_id"] = user_id
                session["_fresh"] = False
            self.reload_user()
    
    def _update_remember_cookie(self, response):
        operation = session.pop("remember", None)
        if operation == "set":
            self._set_cookie(response)
        elif operation == "clear":
            self._clear_cookie(response)
        return response
    
    def _set_cookie(self, response):
        # cookie settings
        config = current_app.config
        cookie_name = config.get("REMEMBER_COOKIE_NAME", COOKIE_NAME)
        duration = config.get("REMEMBER_COOKIE_DURATION", COOKIE_DURATION)
        domain = config.get("REMEMBER_COOKIE_DOMAIN", None)
        # prepare data
        if self.token_callback:
            data = current_user.get_auth_token()
        else:
            data = encode_cookie(session["user_id"])
        expires = datetime.now() + duration
        # actually set it
        response.set_cookie(cookie_name, data, expires=expires, domain=domain)
    
    def _clear_cookie(self, response):
        config = current_app.config
        cookie_name = config.get("REMEMBER_COOKIE_NAME", COOKIE_NAME)
        domain = config.get("REMEMBER_COOKIE_DOMAIN", None)
        response.delete_cookie(cookie_name, domain=domain)


#: A proxy for the current user.
current_user = LocalProxy(lambda: _request_ctx_stack.top.user)

def _user_context_processor():
    return dict(current_user=_request_ctx_stack.top.user)


def login_fresh():
    """
    This returns `True` if the current login is fresh.
    """
    return session.get("_fresh", False)


def login_user(user, remember=False, force=False):
    """
    Logs a user in. You should pass the actual user object to this. If the
    user's `is_active` method returns `False`, they will not be logged in
    unless `force` is `True`.
    
    This will return `True` if the log in attempt succeeds, and `False` if
    it fails (i.e. because the user is inactive).
    
    :param user: The user object to log in.
    :param remember: Whether to remember the user after their session expires.
    :param force: If the user is inactive, setting this to `True` will log
                  them in regardless.
    """
    if (not force) and (not user.is_active()):
        return False
    user_id = user.get_id()
    session["user_id"] = user_id
    session["_fresh"] = True
    if remember:
        session["remember"] = "set"
    app = current_app._get_current_object()
    current_app.login_manager.reload_user()
    user_logged_in.send(current_app._get_current_object(), user=_get_user())
    return True


def logout_user():
    """
    Logs a user out. (You do not need to pass the actual user.) This will
    also clean up the remember me cookie if it exists.
    """
    if "user_id" in session:
        del session["user_id"]
    if "_fresh" in session:
        del session["_fresh"]
    cookie_name = current_app.config.get("REMEMBER_COOKIE_NAME", COOKIE_NAME)
    if cookie_name in request.cookies:
        session["remember"] = "clear"
    user = _get_user()
    if user and (not user.is_anonymous()):
        user_logged_out.send(current_app._get_current_object(), user=user)
    current_app.login_manager.reload_user()
    return True


def confirm_login():
    """
    This sets the current session as fresh. Sessions become stale when they
    are reloaded from a cookie.
    """
    session["_fresh"] = True
    user_login_confirmed.send(current_app._get_current_object())


def login_required(fn):
    """
    If you decorate a view with this, it will ensure that the current user is
    logged in and authenticated before calling the actual view. (If they are
    not, it calls the `~LoginManager.unauthorized` callback.) For example::
    
        @app.route("/post")
        @login_required
        def post():
            pass
    
    If there are only certain times you need to require that your user is
    logged in, you can do so with::
    
        if not current_user.is_authenticated():
            return current_app.login_manager.unauthorized()
    
    (which is essentially the code that this function adds to your views).
    
    :param fn: The view function to decorate.
    """
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated():
            return current_app.login_manager.unauthorized()
        return fn(*args, **kwargs)
    return decorated_view


def fresh_login_required(fn):
    """
    If you decorate a view with this, it will ensure that the current user's
    login is fresh - i.e. there session was not restored from a "remember me"
    cookie. Sensitive operations, like changing a password or e-mail, should
    be protected with this, to impede the efforts of cookie thieves.
    
    If the user is not authenticated, `LoginManager.unauthorized` is called
    as normal. If they are authenticated, but their session is not fresh,
    it will call `LoginManager.needs_refresh` instead. (In that case, you
    will need to provide a `~LoginManager.refresh_view`.)
    
    :param fn: The view function to decorate.
    """
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated():
            return current_app.login_manager.unauthorized()
        elif not login_fresh():
            return current_app.login_manager.needs_refresh()
        return fn(*args, **kwargs)
    return decorated_view


class UserMixin(object):
    """
    This provides default implementations for the methods that Flask-Login
    expects user objects to have.
    """
    def is_active(self):
        """
        Returns `True`.
        """
        return True
    
    def is_authenticated(self):
        """
        Returns `True`.
        """
        return True
    
    def is_anonymous(self):
        """
        Returns `False`.
        """
        return False
    
    def get_id(self):
        """
        Assuming that the user object has an `id` attribute, this will take
        that and convert it to `unicode`.
        """
        try:
            return unicode(self.id)
        except AttributeError:
            raise NotImplementedError("No `id` attribute - override get_id")


class AnonymousUser(object):
    """
    This is the default object for representing an anonymous user.
    """
    def is_authenticated(self):
        return False
    
    def is_active(self):
        return False
    
    def is_anonymous(self):
        return True
    
    def get_id(self):
        return None


# Signals

#: Sent when a user is logged in. In addition to the app (which is the
#: sender), it is passed `user`, which is the user being logged in.
user_logged_in = _signals.signal("logged-in")

#: Sent when a user is logged out. In addition to the app (which is the
#: sender), it is passed `user`, which is the user being logged out.
user_logged_out = _signals.signal("logged-out")

#: Sent when a user's login is confirmed, marking it as fresh. (It is not
#: called for a normal login.)
#: It receives no additional arguments besides the app.
user_login_confirmed = _signals.signal("login-confirmed")

#: Sent when the `unauthorized` method is called on a `LoginManager`. It
#: receives no additional arguments besides the app.
user_unauthorized = _signals.signal("unauthorized")

#: Sent when the `needs_refresh` method is called on a `LoginManager`. It
#: receives no additional arguments besides the app.
user_needs_refresh = _signals.signal("needs-refresh")

#: Sent whenever session protection takes effect, and a session is either
#: marked non-fresh or deleted. It receives no additional arguments besides
#: the app.
session_protected = _signals.signal("session-protected")
