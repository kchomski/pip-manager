# -*- coding: utf-8 -*-
import os

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
