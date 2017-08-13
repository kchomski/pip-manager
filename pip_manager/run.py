# -*- coding: utf-8 -*-
import sys

try:
    import pip
except ImportError:
    sys.exit("'pip' is not installed.")

from pip_manager.app import PipManager


def main():
    PipManager().mainloop()


if __name__ == '__main__':
    main()
