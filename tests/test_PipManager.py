# -*- coding: utf-8 -*-
import curses
import sys
from pip_manager import __version__
from pip_manager import gui
from pip_manager.gui import Gui

import pytest


@pytest.fixture
def fake_instance(mocker):
    _fake_instance = mocker.patch('pip_manager.app.PipManager', autospec=True)
    _fake_instance.stdscr.getmaxyx.return_value = [24, 80]
    # _fake_instance.line_width = 79
    # _fake_instance.menu_height = 12
    # _fake_instance.get_pages_count.return_value = 5
    return _fake_instance


@pytest.fixture
def mocked_curses(mocker):
    _mocked_curses = mocker.patch('pip_manager.app.curses')
    return _mocked_curses


def test_dist_win_height(fake_instance):
    assert hasattr(fake_instance, 'dist_win_height')
