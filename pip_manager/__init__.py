# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import os

logging.basicConfig(
    level=logging.ERROR,
    filename=os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'pip-manager.log'
    ),
    filemode='w',
)

__version__ = '1.0.0'

# TODO: **poprawic architekture (MVC)**
# TODO: unittesty
# TODO: logging
# TODO: Windows http://www.lfd.uci.edu/~gohlke/pythonlibs/#curses
# TODO: link do GH
# TODO: docstringi
# TODO: poprawić dokumentacje (wyswietlanie na BB i GH)
# TODO: yapf, pep8, pylint, pyflakes
# TODO:
