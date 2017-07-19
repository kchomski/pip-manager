# -*- coding: utf-8 -*-
"""

"""
from __future__ import unicode_literals

import curses
import curses.panel
import sys

from contextlib import redirect_stderr
from contextlib import redirect_stdout

from pip_manager import __version__
from pip_manager.const import ENTER
from pip_manager.const import SPACE
from pip_manager.distribution import Distribution
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

    def __init__(self):
        # curses initialization
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(1)
        try:
            curses.start_color()
        except:
            pass
        curses.use_default_colors()

        self.menu_height = len(self.menu_options) + 1  # Plus 1 for menu header
        self.min_height = self.menu_height + 3  # Plus 1 for top header,
        # plus 1 for pages count and 1 to display at least one distribution.

        self.page = self.cursor_pos = 0
        self.popup_win = curses.newwin(3, 20, 1, 0)
        self.panel = curses.panel.new_panel(self.popup_win)
        self.draw_header()
        self.distributions = self.get_distributions()
        self.check_win_size()
        self.dist_win = curses.newwin(
            self.dist_win_height, self.line_width, 1, 0
        )
        self.dist_win.keypad(True)

        self.draw_distributions_list()
        self.draw_page_number()
        self.draw_menu()
        self.mainloop()

    def __del__(self):
        self.stdscr.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()

    @property
    def dist_win_height(self):
        return self.stdscr.getmaxyx()[0] - self.menu_height - 2

    @property
    def dists_to_draw(self):
        start_idx = self.page*self.dist_win_height
        stop_idx = start_idx + self.dist_win_height
        return self.distributions[start_idx:stop_idx]

    @property
    def line_width(self):
        w = (
            4 + max(len(d.name) for d in self.dists_to_draw) + 2 +
            max(len(d.version) for d in self.dists_to_draw) + 2 +
            max(len(d.newest_version) for d in self.dists_to_draw) + 1
        )
        return w

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
            max(len(opt)+len(desc) for opt, desc in self.menu_options),
            self.stdscr.getmaxyx()[0] - self.menu_height,
            0
        )
        win.addstr('Options:\n', curses.A_UNDERLINE)
        for opt, desc in self.menu_options:
            win.addstr(opt, curses.A_BOLD)
            win.addstr(desc)
        win.refresh()

    def get_distributions(self):
        """Gets list of installed distributions along with the newest version
        available.

        :return: List of dicts.
        :rtype: list
        """
        distributions = []
        for d in sorted(pip.get_installed_distributions(), key=lambda x: x.key):
            self.draw_popup('Checking the newest version for {}'.format(d.key))
            distributions.append(Distribution(name=d.key, version=d.version))
        return distributions

    def draw_distributions_list(self):
        """Draws installed distributions.

        Draws installed distributions with current versions installed and
        newest stable versions available.
        """
        selection_mapping = {
            True: 'x',
            False: ' ',
        }

        longest_name = max(len(d.name) for d in self.dists_to_draw)
        longest_version = max(len(d.version) for d in self.dists_to_draw)

        self.dist_win.erase()
        for d in self.dists_to_draw:
            self.dist_win.addstr(
                '[{selection}] {name}{spaces}{version}'.format(
                    selection=selection_mapping[d.is_selected],
                    name=d.name,
                    spaces=' ' * (longest_name - len(d.name) + 2),
                    version=d.version,
                )
            )
            self.dist_win.addstr(
                '{spaces}{newest_ver}'.format(
                    spaces=' ' * (longest_version - len(d.version) + 2),
                    newest_ver=d.newest_version,
                ),
                curses.A_BOLD if d.version != d.newest_version else
                curses.A_DIM
            )
            try:
                self.dist_win.addstr('\n')
            except curses.error:
                pass
        self.dist_win.refresh()

    def toggle_one(self, idx):
        """Toggles selection of currently chosen distribution."""
        self.distributions[idx].is_selected = not self.distributions[idx].is_selected

    def toggle_all(self):
        """Toggles selection of ALL distributions."""
        is_all_checked = all(d.is_selected for d in self.distributions)
        for d in self.distributions:
            d.is_selected = not is_all_checked

    def update_distributions(self):
        """Updates selected distributions to newest stable version available.
        """
        to_update = [d for d in self.distributions if d.is_selected
                     and d.newest_version != 'n/a' and
                     d.version != d.newest_version]
        if to_update:
            for d in to_update:
                self.draw_popup('Upgrading {}'.format(d.name))
                with redirect_stderr(StringIO()), redirect_stdout(StringIO()):
                    pip.main(['install', '--upgrade', d.name])
                d.version = d.newest_version
            for d in self.distributions:
                d.is_selected = False

    def uninstall_distributions(self):
        """Uninstalls selected distributions.

        Does NOT uninstall distributions mentioned in config.ini in [protected]
        section - you either have to remove them manually or remove them from
        config.ini.
        """
        protected = get_protected_dists()
        to_remove = [d for d in self.distributions if d.is_selected
                     and d.name not in protected]
        if to_remove:
            self.draw_popup(
                'Do you really want to remove selected packages? [y/N]'
            )
            if self.stdscr.getch() in (ord('y'), ord('Y')):
                for d in to_remove:
                    self.draw_popup('Removing {}'.format(d.name))
                    with redirect_stderr(StringIO()), redirect_stdout(StringIO()):
                        pip.main(['uninstall', '--yes', d.name])
                    self.distributions.remove(d)

    def draw_popup(self, msg):
        """Draws small bordered window with given message.

        :param str msg: Message to display.
        """
        self.popup_win.erase()
        self.popup_win.refresh()
        self.popup_win.resize(3, max(35, len(msg) + 3))
        self.popup_win.box()
        self.popup_win.addstr(1, 1, msg)
        self.popup_win.refresh()
        self.panel.hide()
        self.panel.hide()
        # self.panel.refresh()
        curses.doupdate()

    def get_pages_count(self):
        """Gets max pages count.

        :return: Max pages count.
        :rtype: int
        """
        return int((len(self.distributions)-1) / self.dist_win_height)

    def check_win_size(self):
        """Checks if terminal has proper size to display all information."""
        while self.dist_win_height < 1:
            self.stdscr.clear()
            self.draw_header()
            self.draw_popup('Please resize the terminal.')
            self.stdscr.getch()
        curses.flushinp()

    def resize_dist_win(self):
        self.dist_win.erase()
        self.dist_win.resize(self.dist_win_height, self.line_width)
        self.dist_win.refresh()

    @property
    def max_cursor_pos(self):
        """Gets maximum cursor position for current page to be in distributions
        list range.

        :return: Maximum cursor position available.
        :rtype: int
        """
        try:
            _ = self.distributions[self.dist_win_height*(self.page + 1)]
        except IndexError:
            return len(self.distributions) - 1 - self.page * self.dist_win_height
        return self.dist_win_height - 1

    def mainloop(self):
        """Main program loop."""
        while True:
            self.draw_distributions_list()
            self.dist_win.chgat(self.cursor_pos, 3, curses.A_REVERSE)
            self.dist_win.move(self.cursor_pos, 1)
            self.dist_win.refresh()

            try:
                key = self.dist_win.getch()
            except KeyboardInterrupt:
                break

            if key == curses.KEY_UP:
                self.cursor_pos = max(self.cursor_pos - 1, 0)
            elif key == curses.KEY_DOWN:
                self.cursor_pos = min(self.cursor_pos + 1, self.max_cursor_pos)
            elif key == curses.KEY_HOME:
                self.cursor_pos = 0
            elif key == curses.KEY_END:
                self.cursor_pos = self.max_cursor_pos
            elif key == curses.KEY_PPAGE:
                self.cursor_pos = max(self.cursor_pos-5, 0)
            elif key == curses.KEY_NPAGE:
                self.cursor_pos = min(self.cursor_pos + 5, self.max_cursor_pos)
            elif key in (ord('q'), ord('Q')):
                break
            else:
                if key == curses.KEY_LEFT:
                    self.page = max(self.page-1, 0)
                elif key == curses.KEY_RIGHT:
                    self.page = min(self.page+1, self.get_pages_count())
                elif key == SPACE:
                    curr_dist_idx = self.page * self.dist_win_height + self.cursor_pos
                    self.toggle_one(curr_dist_idx)
                elif key in (ord('a'), ord('A')):
                    self.toggle_all()
                elif key == ENTER:
                    self.update_distributions()
                elif key == curses.KEY_DC:
                    self.uninstall_distributions()
                elif key == curses.KEY_RESIZE:
                    self.check_win_size()
                self.resize_dist_win()
                self.cursor_pos = min(self.cursor_pos, self.max_cursor_pos)
                self.draw_page_number(self.page)
                self.draw_menu()
