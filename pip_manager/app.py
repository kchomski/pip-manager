# -*- coding: utf-8 -*-
"""

"""
from __future__ import unicode_literals

import curses
import sys

try:
    from contextlib import redirect_stderr
    from contextlib import redirect_stdout
except ImportError:
    from pip_manager.utils import redirect_stderr
    from pip_manager.utils import redirect_stdout


from pip_manager.gui import Gui
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
        self.page = self.cursor_pos = 0
        self.gui = Gui(79)
        self.distributions = self.get_distributions()
        self.mainloop()

    @property
    def dists_to_draw(self):
        """

        :return:
        """
        start_idx = self.page * self.gui.dist_win_height
        stop_idx = start_idx + self.gui.dist_win_height
        return self.distributions[start_idx:stop_idx]

    def get_distributions(self):
        """Gets list of installed distributions.

        :return: List of installed distributions.
        :rtype: list
        """
        distributions = []
        for d in sorted(pip.get_installed_distributions(), key=lambda x: x.key):
            self.gui.draw_popup(
                'Checking the newest version for {}'.format(d.key)
            )
            distributions.append(Distribution(name=d.key, version=d.version))
        return distributions

    def toggle_one(self, idx):
        """Toggles selection of currently chosen distribution."""
        self.distributions[
            idx
        ].is_selected = not self.distributions[idx].is_selected

    def toggle_all(self):
        """Toggles selection of ALL distributions."""
        is_all_checked = all(d.is_selected for d in self.distributions)
        for d in self.distributions:
            d.is_selected = not is_all_checked

    def update_distributions(self):
        """Updates selected distributions to newest stable version available.
        """
        to_update = [
            d for d in self.distributions
            if d.is_selected and d.newest_version != 'n/a' and
            d.version != d.newest_version
        ]
        if to_update:
            for d in to_update:
                self.gui.draw_popup('Upgrading {}'.format(d.name))
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
        to_remove = [
            d for d in self.distributions
            if d.is_selected and d.name not in protected
        ]
        if to_remove:
            self.gui.draw_popup(
                'Do you really want to remove selected packages? [y/N]'
            )
            if self.gui.stdscr.getch() in (ord('y'), ord('Y')):
                for d in to_remove:
                    self.gui.draw_popup('Removing {}'.format(d.name))
                    with redirect_stderr(StringIO()
                                        ), redirect_stdout(StringIO()):
                        pip.main(['uninstall', '--yes', d.name])
                    self.distributions.remove(d)

    @property
    def last_page(self):
        """Gets max pages count.

        :return: Max pages count.
        :rtype: int
        """
        return int((len(self.distributions) - 1) / self.gui.dist_win_height)

    def mainloop(self):
        """Main program loop."""
        while True:
            max_cursor_pos = len(self.dists_to_draw) - 1
            self.cursor_pos = min(self.cursor_pos, max_cursor_pos)
            self.gui.draw_distributions_list(
                self.dists_to_draw,
                self.page + 1,
                self.last_page + 1,
                self.cursor_pos
            )

            try:
                key = self.gui.dist_win.getch()
            except KeyboardInterrupt:
                break

            if key == curses.KEY_UP:
                self.cursor_pos = max(self.cursor_pos - 1, 0)
            elif key == curses.KEY_DOWN:
                self.cursor_pos = min(self.cursor_pos + 1, max_cursor_pos)
            elif key == curses.KEY_HOME:
                self.cursor_pos = 0
            elif key == curses.KEY_END:
                self.cursor_pos = max_cursor_pos
            elif key == curses.KEY_PPAGE:
                self.cursor_pos = max(self.cursor_pos - 5, 0)
            elif key == curses.KEY_NPAGE:
                self.cursor_pos = min(self.cursor_pos + 5, max_cursor_pos)
            elif key in (ord('q'), ord('Q')):
                break
            elif key == curses.KEY_LEFT:
                self.page = max(self.page - 1, 0)
            elif key == curses.KEY_RIGHT:
                self.page = min(self.page + 1, self.last_page)
            elif key == SPACE:
                curr_dist_idx = (
                    self.page * self.gui.dist_win_height + self.cursor_pos
                )
                self.toggle_one(curr_dist_idx)
            elif key in (ord('a'), ord('A')):
                self.toggle_all()
            elif key == ENTER:
                self.update_distributions()
            elif key == curses.KEY_DC:
                self.uninstall_distributions()
            elif key == curses.KEY_RESIZE:
                self.gui.check_win_size()
