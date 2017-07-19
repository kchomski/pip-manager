# -*- coding: utf-8 -*-
"""

"""
import pip
import re
import sys

from contextlib import redirect_stderr
from contextlib import redirect_stdout

if sys.version_info.major == 2:
    from StringIO import StringIO
else:
    from io import StringIO


class Distribution(object):

    def __init__(self, name, version):
        self.name = name
        self.version = version
        self.newest_version = self.get_newest_version()
        self.is_selected = False

    def get_newest_version(self):
        """Gets newest version of distribution available.

        Returns newest *stable* version if available (assumption is that stable
        version consists of only numbers separated by dots (e.g. 1.9.23)).
        If not returns newest version available (e.g. 3.2.3.post2).
        If version cannot be determined 'n/a' is returned.

        :return: Newest version.
        :rtype: str
        """
        err_stream = StringIO()
        with redirect_stderr(err_stream), redirect_stdout(StringIO()):
            pip.main(['install', '{}=='.format(self.name)])
        versions = [
            ver for ver in re.findall(
                r'[\d\.]+[\d]*[\w]*',
                err_stream.getvalue().split('\n')[0].split('(')[-1]
            )
        ]
        try:
            return [v for v in versions if v.replace('.', '').isdigit()][-1]
        except IndexError:
            try:
                return versions[-1]
            except IndexError:
                return 'n/a'
