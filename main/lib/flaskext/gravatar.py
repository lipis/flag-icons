# coding: utf-8

import hashlib

class Gravatar(object):
    """Simple object for create gravatar link.

        gravatar = Gravatar(app,
                            size=100,
                            rating='g',
                            default='retro',
                            force_default=False,
                            force_lower=False,
                            use_ssl=False
                           )

    :param app: Your Flask app instance
    :param size: Default size for avatar
    :param rating: Default rating
    :param default: Default type for unregistred emails
    :param force_default: Build only default avatars
    :param force_lower: Make email.lower() before build link
    :param use_ssl: Use https rather than http
    
    """

    def __init__(self, app, size=100, rating='g', default='retro',
                 force_default=False, force_lower=False, use_ssl=False):

        self.size = size
        self.rating = rating
        self.default = default
        self.force_default = force_default
        self.use_ssl = use_ssl

        app.jinja_env.filters.setdefault('gravatar', self)

    def __call__(self, email, size=None, rating=None, default=None,
                 force_default=None, force_lower=False, use_ssl=None):

        """Build gravatar link."""

        if size is None:
            size = self.size

        if rating is None:
            rating = self.rating

        if default is None:
            default = self.default

        if force_default is None:
            force_default = self.force_default

        if force_lower is None:
            force_lower = self.force_lower

        if force_lower:
            email = email.lower()
            
        if use_ssl is None:
            use_ssl = self.use_ssl
        
        if use_ssl:
            url = 'https://gravatar.com/avatar/'
        else:
            url = 'http://gravatar.com/avatar/'

        hash = hashlib.md5(email).hexdigest()

        link = '{url}{hash}'\
               '?s={size}&d={default}&r={rating}'.format(**locals())

        if force_default:
            link = link + '&f=y'

        return link