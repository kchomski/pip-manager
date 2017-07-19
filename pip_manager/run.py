# -*- coding: utf-8 -*-
import curses

from pip_manager.app import PipManager


def main():
    curses.wrapper(PipManager)


if __name__ == '__main__':
    main()
