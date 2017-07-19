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

# TODO: unittesty
# TODO: logging
# TODO: Windows http://www.lfd.uci.edu/~gohlke/pythonlibs/#curses
# TODO: link do GH
# TODO: **poprawic architekture**
# TODO: docstringi
# TODO: poprawić dokumentacje (wyswietlanie na BB i GH)
# TODO:
