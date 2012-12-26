# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2008 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://babel.edgewall.org/wiki/License.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://babel.edgewall.org/log/.

"""Integrated collection of utilities that assist in internationalizing and
localizing applications.

This package is basically composed of two major parts:

 * tools to build and work with ``gettext`` message catalogs
 * a Python interface to the CLDR (Common Locale Data Repository), providing
   access to various locale display names, localized number and date
   formatting, etc.

:see: http://www.gnu.org/software/gettext/
:see: http://docs.python.org/lib/module-gettext.html
:see: http://www.unicode.org/cldr/
"""

from babel.core import *

__docformat__ = 'restructuredtext en'
try:
    from pkg_resources import get_distribution, ResolutionError
    try:
        __version__ = get_distribution('Babel').version
    except ResolutionError:
        __version__ = None # unknown
except ImportError:
    __version__ = None # unknown
