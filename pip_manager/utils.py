# -*- coding: utf-8 -*-
import functools
import os
import sys

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

if sys.version_info.major == 2:
    from StringIO import StringIO
else:
    from io import StringIO


def suppress_std_stream(stream):
    """Redirects given stream to StringIO.

    :param str stream: Stream name to suppress.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if stream == 'stdout':
                sys.stdout = StringIO()
            elif stream == 'stderr':
                sys.stderr = StringIO()
            try:
                return func(*args, **kwargs)
            finally:
                sys.stdout, sys.stderr = sys.__stdout__, sys.__stderr__
        return wrapper
    return decorator


def get_protected_dists():
    """Gets list of protected distributions from config.ini file.

    :return: List of string with names of protected distributions.
    :rtype: list
    """
    parser = ConfigParser()
    parser.read(os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'config.ini')
    )
    return parser.options('protected')
