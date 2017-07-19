# -*- coding: utf-8 -*-
"""

"""
from __future__ import unicode_literals

import curses
import re
import sys

from pip_manager import __version__
from pip_manager.const import ENTER, SPACE
from pip_manager.utils import suppress_std_stream
from pip_manager.utils import get_protected_dists

try:
    import pip
except ImportError:
    sys.exit("'pip' is not installed.")

try:
    from importlib import reload
except ImportError:
    pass

if sys.version_info.major == 2:
    from StringIO import StringIO
else:
    from io import StringIO


class PipManager(object):

    line_width = 79
    menu_options = [
        ('Up/Down', ' - prev/next package\n'),
        ('Left/Right', ' - prev/next page\n'),
        ('PgUp/PgDn', ' - jump up/down by 5\n'),
        ('Home/End', ' - jump to top/bottom\n'),
        ('Space', ' - (un)select package\n'),
        ('A', ' - toggle all\n'),
        ('Enter', ' - upgrade selected\n'),
        ('Delete', ' - uninstall selected\n'),
        ('Q', ' - exit'),
    ]

    def __init__(self, stdscr):
        curses.use_default_colors()
        self.stdscr = stdscr
        self.menu_height = len(self.menu_options) + 1  # Plus 1 for menu header
        self.min_height = self.menu_height + 3  # Plus 1 for top header,
        # plus 1 for pages count and 1 to display at least one distribution.

        self.draw_header()
        self.distributions = self.get_distributions()
        self.check_terminal_size()

        self.dist_win = self.get_dist_window()
        self.draw_distributions_list()
        self.draw_page_number()
        self.draw_menu()
        self.mainloop()

    def get_dist_window(self):
        """Returns window used to draw distributions list.

        :return: curses window instance.
        """
        win_height = self.stdscr.getmaxyx()[0] - self.menu_height - 2
        win = curses.newwin(win_height, self.line_width, 1, 0)
        win.keypad(True)
        return win

    def draw_header(self):
        """Draws top most header with program name and python version."""
        self.stdscr.addstr(
            0, 0, 'pip-manager v{} (python {})'.format(
                __version__, sys.version.split()[0]), curses.A_BOLD
        )
        self.stdscr.refresh()

    def draw_page_number(self, page=0):
        """Draws page number under distributions list.

        :param int page: Current page number.
        """
        win = curses.newwin(
            1,
            self.line_width,
            self.stdscr.getmaxyx()[0] - self.menu_height - 1,
            0
        )
        win.addstr('Page: {}/{}'.format(page + 1, self.get_pages_count() + 1))
        win.refresh()

    def draw_menu(self):
        """Draws options menu at the bottom of the terminal."""
        win = curses.newwin(
            self.menu_height,
            self.line_width,
            self.stdscr.getmaxyx()[0] - self.menu_height,
            0
        )
        win.addstr('Options:\n', curses.A_UNDERLINE)
        for opt, desc in self.menu_options:
            win.addstr(opt, curses.A_BOLD)
            win.addstr(desc)
        win.refresh()

    @suppress_std_stream('stdout')
    def get_newest_version(self, dist_name):
        """Gets newest version of *dist_name*.

        Returns newest *stable* version if available (assumption is that stable
        version consists of only numbers separated by dots (e.g. 1.9.23)).
        If not returns newest version available (e.g. 3.2.3.post2).
        If version cannot be determined 'n/a' is returned.

        :param str dist_name: Name of distribution to check.
        :return: Newest version.
        :rtype: str
        """
        sys.stderr = StringIO()
        self.draw_popup('Checking the newest version for {}'.format(dist_name))
        pip.main(['install', '{}=='.format(dist_name)])
        err = sys.stderr
        versions = [
            ver for ver in re.findall(
                r'[\d\.]+[\d]*[\w]*',
                err.getvalue().split('\n')[0].split('(')[-1]
            )
        ]
        try:
            return [v for v in versions if v.replace('.', '').isdigit()][-1]
        except IndexError:
            try:
                return versions[-1]
            except IndexError:
                return 'n/a'

    def get_distributions(self):
        """Gets list of installed distributions along with the newest version
        available.

        :return: List of dicts.
        :rtype: list
        """
        # reload is needed, so pip can get current versions of installed
        # packages after they are updated.
        reload(pip.utils.pkg_resources)
        distributions = [
            {
                'name': d.key,
                'curr_ver': d.version,
                'newest_ver': self.get_newest_version(d.key),
                'is_checked': False
            } for d in sorted(
                pip.get_installed_distributions(), key=lambda x: x.key
            )
        ]
        return distributions

    def draw_distributions_list(self, start_idx=0):
        """Draws installed distributions.

        Draws installed distributions with current versions installed and
        newest stable versions available.

        :param int start_idx: Starting index.
        """
        selection_mapping = {
            True: 'x',
            False: ' ',
        }

        stop_idx = start_idx + self.dist_win.getmaxyx()[0]
        dist_to_draw = self.distributions[start_idx:stop_idx]

        dist_name_offset = 4
        curr_ver_offset = (
            dist_name_offset + max(len(d['name']) for d in dist_to_draw) + 1
        )
        newest_ver_offset = (
            curr_ver_offset + max(len(d['curr_ver']) for d in dist_to_draw) + 2
        )

        self.dist_win.erase()
        for d in dist_to_draw:
            y = self.dist_win.getyx()[0]
            self.dist_win.addstr(
                '[{}]'.format(selection_mapping[d['is_checked']])
            )
            self.dist_win.addstr(y, dist_name_offset, d['name'])
            self.dist_win.addstr(y, curr_ver_offset, d['curr_ver'])
            self.dist_win.addstr(
                y, newest_ver_offset, d['newest_ver'],
                curses.A_BOLD if d['curr_ver'] != d['newest_ver'] else
                curses.A_DIM
            )
            try:
                self.dist_win.addstr('\n')
            except curses.error:
                pass
        self.dist_win.refresh()

    def toggle_one(self, idx):
        """Toggles selection of currently chosen distribution."""
        self.distributions[idx]['is_checked'] = (
            True if not self.distributions[idx]['is_checked'] else False
        )

    def toggle_all(self):
        """Toggles selection of ALL distributions."""
        is_all_checked = all(d['is_checked'] for d in self.distributions)
        for d in self.distributions:
            d['is_checked'] = True if not is_all_checked else False

    @suppress_std_stream('stdout')
    @suppress_std_stream('stderr')
    def update_distributions(self):
        """Updates selected distributions to newest stable version available.
        """
        to_update = [d for d in self.distributions if d['is_checked']
                     and d['newest_ver'] != 'n/a' and
                     d['curr_ver'] != d['newest_ver']]
        if to_update:
            for d in to_update:
                self.draw_popup('Upgrading {}'.format(d['name']))
                pip.main(['install', '--upgrade', d['name']])
                d['curr_ver'] = d['newest_ver']
            for d in self.distributions:
                d['is_checked'] = False

    @suppress_std_stream('stdout')
    @suppress_std_stream('stderr')
    def uninstall_distributions(self):
        """Uninstalls selected distributions.

        Does NOT uninstall distributions mentioned in config.ini in [protected]
        section - you either have to remove them manually or remove them from
        config.ini.
        """
        protected = get_protected_dists()
        to_remove = [d for d in self.distributions if d['is_checked']
                     and d['name'] not in protected]
        if to_remove:
            self.draw_popup(
                'Do you really want to remove selected packages? [y/N]'
            )
            if self.stdscr.getch() in (ord('y'), ord('Y')):
                for d in to_remove:
                    self.draw_popup('Removing {}'.format(d['name']))
                    pip.main(['uninstall', '--yes', d['name']])
                    self.distributions.remove(d)

    def draw_popup(self, msg):
        """Draws small bordered window with given message.

        :param str msg: Message to display.
        """
        win = curses.newwin(3, self.line_width, 1, 0)
        win.box()
        win.addstr(1, 1, msg)
        win.refresh()

    def get_pages_count(self):
        """Gets max pages count.

        :return: Max pages count.
        :rtype: int
        """
        return int((len(self.distributions)-1) / (self.dist_win.getmaxyx()[0]))

    def check_terminal_size(self):
        """Checks if terminal has proper size to display all information."""
        while self.stdscr.getmaxyx()[0] < self.min_height:
            self.stdscr.clear()
            self.draw_header()
            self.draw_popup('Please resize the terminal.')
            self.stdscr.getch()
        curses.flushinp()

    def get_max_cursor_pos(self, page):
        """Gets maximum cursor position for current page to be in distributions
        list range.

        :param int page: Current page.
        :return: Maximum cursor position available.
        :rtype: int
        """
        win_height = self.dist_win.getmaxyx()[0]
        try:
            _ = self.distributions[win_height*(page + 1)]
        except IndexError:
            return len(self.distributions) - 1 - page * win_height
        return win_height - 1

    def mainloop(self):
        """Main program loop."""
        page = cursor_pos = 0

        while True:
            win_height = self.dist_win.getmaxyx()[0]
            curr_dist_idx = page * win_height + cursor_pos

            self.dist_win.chgat(cursor_pos, 3, curses.A_REVERSE)
            self.dist_win.move(cursor_pos, 1)
            self.dist_win.refresh()

            try:
                key = self.dist_win.getch()
            except KeyboardInterrupt:
                break

            if key == curses.KEY_UP:
                cursor_pos = max(cursor_pos - 1, 0)
            elif key == curses.KEY_DOWN:
                cursor_pos = min(cursor_pos + 1, self.get_max_cursor_pos(page))
            elif key == curses.KEY_HOME:
                cursor_pos = 0
            elif key == curses.KEY_END:
                cursor_pos = self.get_max_cursor_pos(page)
            elif key == curses.KEY_PPAGE:
                cursor_pos = max(cursor_pos-5, 0)
            elif key == curses.KEY_NPAGE:
                cursor_pos = min(cursor_pos + 5, self.get_max_cursor_pos(page))
            elif key in (ord('q'), ord('Q')):
                break
            else:
                if key == curses.KEY_LEFT:
                    page = max(page-1, 0)
                elif key == curses.KEY_RIGHT:
                    page = min(page+1, self.get_pages_count())
                elif key == SPACE:
                    self.toggle_one(curr_dist_idx)
                elif key in (ord('a'), ord('A')):
                    self.toggle_all()
                elif key == ENTER:
                    self.update_distributions()
                elif key == curses.KEY_DC:
                    self.uninstall_distributions()
                elif key == curses.KEY_RESIZE:
                    self.check_terminal_size()
                    self.dist_win = self.get_dist_window()
                cursor_pos = min(cursor_pos, self.get_max_cursor_pos(page))
                self.draw_page_number(page)
                self.draw_menu()
            self.draw_distributions_list(win_height * page)
