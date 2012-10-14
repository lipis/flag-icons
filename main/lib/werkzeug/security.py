# -*- coding: utf-8 -*-
"""
    werkzeug.security
    ~~~~~~~~~~~~~~~~~

    Security related helpers such as secure password hashing tools.

    :copyright: (c) 2011 by the Werkzeug Team, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""
import os
import hmac
import posixpath
from itertools import izip
from random import SystemRandom

# because the API of hmac changed with the introduction of the
# new hashlib module, we have to support both.  This sets up a
# mapping to the digest factory functions and the digest modules
# (or factory functions with changed API)
try:
    from hashlib import sha1, md5
    _hash_funcs = _hash_mods = {'sha1': sha1, 'md5': md5}
    _sha1_mod = sha1
    _md5_mod = md5
except ImportError:
    import sha as _sha1_mod, md5 as _md5_mod
    _hash_mods = {'sha1': _sha1_mod, 'md5': _md5_mod}
    _hash_funcs = {'sha1': _sha1_mod.new, 'md5': _md5_mod.new}


SALT_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'


_sys_rng = SystemRandom()
_os_alt_seps = list(sep for sep in [os.path.sep, os.path.altsep]
                    if sep not in (None, '/'))


def safe_str_cmp(a, b):
    """This function compares strings in somewhat constant time.  This
    requires that the length of at least one string is known in advance.

    Returns `True` if the two strings are equal or `False` if they are not.

    .. versionadded:: 0.7
    """
    if len(a) != len(b):
        return False
    rv = 0
    for x, y in izip(a, b):
        rv |= ord(x) ^ ord(y)
    return rv == 0


def gen_salt(length):
    """Generate a random string of SALT_CHARS with specified ``length``."""
    if length <= 0:
        raise ValueError('requested salt of length <= 0')
    return ''.join(_sys_rng.choice(SALT_CHARS) for _ in xrange(length))


def _hash_internal(method, salt, password):
    """Internal password hash helper.  Supports plaintext without salt,
    unsalted and salted passwords.  In case salted passwords are used
    hmac is used.
    """
    if method == 'plain':
        return password
    if salt:
        if method not in _hash_mods:
            return None
        if isinstance(salt, unicode):
            salt = salt.encode('utf-8')
        h = hmac.new(salt, None, _hash_mods[method])
    else:
        if method not in _hash_funcs:
            return None
        h = _hash_funcs[method]()
    if isinstance(password, unicode):
        password = password.encode('utf-8')
    h.update(password)
    return h.hexdigest()


def generate_password_hash(password, method='sha1', salt_length=8):
    """Hash a password with the given method and salt with with a string of
    the given length.  The format of the string returned includes the method
    that was used so that :func:`check_password_hash` can check the hash.

    The format for the hashed string looks like this::

        method$salt$hash

    This method can **not** generate unsalted passwords but it is possible
    to set the method to plain to enforce plaintext passwords.  If a salt
    is used, hmac is used internally to salt the password.

    :param password: the password to hash
    :param method: the hash method to use (``'md5'`` or ``'sha1'``)
    :param salt_length: the lengt of the salt in letters
    """
    salt = method != 'plain' and gen_salt(salt_length) or ''
    h = _hash_internal(method, salt, password)
    if h is None:
        raise TypeError('invalid method %r' % method)
    return '%s$%s$%s' % (method, salt, h)


def check_password_hash(pwhash, password):
    """check a password against a given salted and hashed password value.
    In order to support unsalted legacy passwords this method supports
    plain text passwords, md5 and sha1 hashes (both salted and unsalted).

    Returns `True` if the password matched, `False` otherwise.

    :param pwhash: a hashed string like returned by
                   :func:`generate_password_hash`
    :param password: the plaintext password to compare against the hash
    """
    if pwhash.count('$') < 2:
        return False
    method, salt, hashval = pwhash.split('$', 2)
    return safe_str_cmp(_hash_internal(method, salt, password), hashval)


def safe_join(directory, filename):
    """Safely join `directory` and `filename`.  If this cannot be done,
    this function returns ``None``.

    :param directory: the base directory.
    :param filename: the untrusted filename relative to that directory.
    """
    filename = posixpath.normpath(filename)
    for sep in _os_alt_seps:
        if sep in filename:
            return None
    if os.path.isabs(filename) or filename.startswith('../'):
        return None
    return os.path.join(directory, filename)
