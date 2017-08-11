# -*- coding: utf-8 -*-
import os
import sys

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser


def get_protected_dists():
    """Gets list of protected distributions from config.ini file.

    :return: List with names of protected distributions.
    :rtype: list
    """
    parser = ConfigParser()
    parser.read(
        os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.ini')
    )
    return parser.options('protected')


class _RedirectStream(object):

    _stream_name = None

    def __init__(self, new_stream_obj):
        self.old_stream_obj = getattr(sys, self._stream_name)
        self.new_stream_obj = new_stream_obj

    def __enter__(self):
        setattr(sys, self._stream_name, self.new_stream_obj)
        return self.new_stream_obj

    def __exit__(self, exc_type, exc_val, exc_tb):
        setattr(sys, self._stream_name, self.old_stream_obj)


class redirect_stdout(_RedirectStream):
    _stream_name = 'stdout'


class redirect_stderr(_RedirectStream):
    _stream_name = 'stderr'
