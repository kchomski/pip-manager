# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import os

logging.basicConfig(
    level=logging.ERROR,
    filename=os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'pypackt.log'
    ),
    filemode='w',
)

__version__ = '1.0.0'

# TODO: Windows http://www.lfd.uci.edu/~gohlke/pythonlibs/#curses
# TODO: unittesty
# TODO: logging
# TODO: link do GH
# TODO:
