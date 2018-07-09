# -*- coding: utf-8 -*-
import curses
import sys

from pip_manager import __version__


class Gui(object):

    stdscr = None

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

    def __init__(self, line_width):
        self.line_width = line_width
        self._initialize_curses()
        self.menu_height = len(self.menu_options) + 1
        self.min_height = self.menu_height + 3
        self.popup_win = curses.newwin(3, 20, 1, 0)
        self._draw_header()
        self.check_win_size()
        self.dist_win = curses.newwin(
            self.dist_win_height, self.line_width, 1, 0
        )
        self.dist_win.keypad(True)

    def _initialize_curses(self):
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(1)
        try:
            curses.start_color()
        except curses.error:
            pass
        curses.use_default_colors()

    def __del__(self):
        """Cleanup."""
        self.stdscr.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()

    @property
    def dist_win_height(self):
        """Returns distributions list window height.

        :return: Distributions list window height.
        :rtype: int
        """
        return self.stdscr.getmaxyx()[0] - self.menu_height - 2

    def _draw_header(self):
        """Draws top most header with program name and python version."""
        self.stdscr.addstr(
            0, 0, 'pip-manager {} (python {})'.format(
                __version__, sys.version.split()[0]
            ), curses.A_BOLD
        )
        self.stdscr.refresh()

    def _draw_page_number(self, curr_page, last_page):
        """Draws page number under distributions list."""
        win = curses.newwin(
            1, self.line_width,
            self.stdscr.getmaxyx()[0] - self.menu_height - 1, 0
        )
        win.addstr('Page: {}/{}'.format(curr_page, last_page))
        win.refresh()

    def _draw_menu(self):
        """Draws options menu at the bottom of the terminal."""
        win = curses.newwin(
            self.menu_height, self.line_width,
            self.stdscr.getmaxyx()[0] - self.menu_height, 0
        )
        win.addstr('Options:\n', curses.A_UNDERLINE)
        for opt, desc in self.menu_options:
            win.addstr(opt, curses.A_BOLD)
            win.addstr(desc)
        win.refresh()

    def draw_distributions(self, dists_to_draw, page, last_page, cursor_pos):
        self._resize_dist_win()
        self._draw_distributions_list(dists_to_draw)
        self._draw_page_number(page, last_page)
        self._draw_menu()
        self.dist_win.chgat(cursor_pos, 3, curses.A_REVERSE)
        self.dist_win.move(cursor_pos, 1)

    def _draw_distributions_list(self, dists_to_draw):
        """Draws distributions list.

        Draws list of distributions with their current versions and newest
        versions available.
        """
        selection_mapping = {
            True: 'x',
            False: ' ',
        }

        longest_name = max(len(d.name) for d in dists_to_draw)
        longest_version = max(len(d.version) for d in dists_to_draw)

        self.dist_win.erase()
        for d in dists_to_draw:
            self.dist_win.addstr(
                '[{is_selected}] {name}{spaces}{version}'.format(
                    is_selected=selection_mapping[d.is_selected],
                    name=d.name,
                    spaces=' ' * (longest_name - len(d.name) + 2),
                    version=d.version,
                )
            )
            self.dist_win.addstr(
                '{spaces}{newest_ver}'.format(
                    spaces=' ' * (longest_version - len(d.version) + 2),
                    newest_ver=d.newest_version,
                ), curses.A_BOLD
                if d.version != d.newest_version else curses.A_DIM
            )
            try:
                self.dist_win.addstr('\n')
            except curses.error:
                pass
        self.dist_win.refresh()

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

    def check_win_size(self):
        """Checks if terminal has proper size to display all information."""
        while self.dist_win_height < 1:
            self.stdscr.clear()
            self._draw_header()
            self.draw_popup('Please resize the terminal.')
            self.stdscr.getch()
        curses.flushinp()

    def _resize_dist_win(self):
        self.dist_win.erase()
        self.dist_win.resize(self.dist_win_height, self.line_width)
        self.dist_win.refresh()
