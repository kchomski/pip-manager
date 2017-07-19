# -*- coding: utf-8 -*-
import curses
import sys
from pip_manager import __version__
from pip_manager import app
from pip_manager.app import PipManager

import pytest


@pytest.fixture
def fake_instance(mocker):
    _fake_instance = mocker.Mock(autospec='pip_manager.app.PipManager')
    _fake_instance.stdscr.getmaxyx.return_value = [24, 80]
    _fake_instance.line_width = 79
    _fake_instance.menu_height = 12
    _fake_instance.get_pages_count.return_value = 5
    return _fake_instance


@pytest.fixture
def mocked_curses(mocker):
    _mocked_curses = mocker.patch('pip_manager.app.curses')
    return _mocked_curses


@pytest.fixture
def mocked_pip(mocker):
    _mocked_pip = mocker.patch('pip_manager.app.pip')

    class Distribution(object):
        def __init__(self, name, version):
            self.key = name
            self.version = version

    _mocked_pip.get_installed_distributions.return_value = [
        Distribution('wheel', '0.29.0'),
        Distribution('pip', '0.9.1'),
        Distribution('flask', '0.12'),
        Distribution('setuptools', '36.1.2'),
    ]

    return _mocked_pip


def test_get_dist_window(mocked_curses, fake_instance):
    rv = PipManager.get_dist_window(fake_instance)
    mocked_curses.newwin.assert_called_with(10, 79, 1, 0)
    mocked_curses.newwin.return_value.keypad.assert_called_with(True)
    assert rv == mocked_curses.newwin.return_value


def test_draw_header(fake_instance):
    PipManager.draw_header(fake_instance)
    fake_instance.stdscr.addstr.assert_called_with(
        0, 0, 'pip-manager v{} (python {})'.format(
                __version__, sys.version.split()[0]
        ), curses.A_BOLD
    )
    assert fake_instance.stdscr.refresh.called


def test_draw_page_number(mocked_curses, fake_instance):
    PipManager.draw_page_number(fake_instance, 0)
    mocked_curses.newwin.assert_called_with(1, 79, 11, 0)
    mocked_curses.newwin.return_value.addstr.assert_called_with('Page: 1/6')
    assert mocked_curses.newwin.return_value.refresh.called


@pytest.mark.parametrize(
    'pip_output, expected',
    [
        ('Fake msg with flask version (0.9, 0.10, 0.12)\nFatal error', '0.12'),
        ('Fake msg with flask version (0.10, 0.12a1)\nFatal error', '0.10'),
        ('Fake msg with flask version (0.9a, 0.10a)\nFatal error', '0.10a'),
        ('Fake msg with flask version ()\nFatal error', 'n/a'),
        ('Fake msg with flask version (a, b, c)\nFatal error', 'n/a'),
    ]
)
def test_get_newest_stable_version(
        mocker, fake_instance, mocked_pip, pip_output, expected):
    dist = 'flask'
    mocked_stringio = mocker.patch('pip_manager.app.StringIO')
    mocked_stringio.return_value.getvalue.return_value = pip_output

    rv = PipManager.get_newest_version(fake_instance, dist)
    fake_instance.draw_popup.assert_called_with(
        'Checking the newest version for {}'.format(dist)
    )
    mocked_pip.main.assert_called_with(['install', '{}=='.format(dist)])
    assert mocked_stringio.return_value.getvalue.called
    assert rv == expected


def test_get_distributions(mocker, mocked_pip, fake_instance):
    mocked_reload = mocker.patch('pip_manager.app.reload')
    fake_instance.get_newest_version.return_value = '101.1.9'
    rv = PipManager.get_distributions(fake_instance)
    assert mocked_reload.called
    assert rv == [
        {'name': 'flask',
         'curr_ver': '0.12',
         'newest_ver': '101.1.9',
         'is_checked': False},
        {'name': 'pip',
         'curr_ver': '0.9.1',
         'newest_ver': '101.1.9',
         'is_checked': False},
        {'name': 'setuptools',
         'curr_ver': '36.1.2',
         'newest_ver': '101.1.9',
         'is_checked': False},
        {'name': 'wheel',
         'curr_ver': '0.29.0',
         'newest_ver': '101.1.9',
         'is_checked': False}
    ]
