# -*- coding: utf-8 -*-
import re
import subprocess
import sys

from subprocess import CalledProcessError
from subprocess import STDOUT


class Distribution(object):
    def __init__(self, name, version):
        self.name = name
        self.version = version
        self.newest_version = self.get_newest_version()
        self.is_selected = False

    def __str__(self):
        return '<Distribution({}|{}|{})>'.format(
            self.name, self.version, self.newest_version
        )

    def __repr__(self):
        return '<Distribution({}|{}|{})>'.format(
            self.name, self.version, self.newest_version
        )

    def __eq__(self, other):
        return self.name == other.name and self.version == other.version

    def get_newest_version(self):
        """Gets newest version of distribution available.

        Returns newest *stable* version if available (assumption is that stable
        version consists of only numbers separated by dots (e.g. 1.9.23)).
        If not returns newest version available (e.g. 3.2.3.post2).
        If version cannot be determined 'n/a' is returned.

        :return: Newest version.
        :rtype: str
        """
        error_msg = 'n/a'
        try:
            subprocess.check_output([sys.executable, '-m', 'pip', 'install', '{}==lxPhr_ffmS3fZ3E4P7U1Lw'.format(self.name)], stderr=STDOUT)  # noqa: E501 line too long
        except CalledProcessError as e:
            error_msg = e.output.decode()

        versions = [
            ver
            for ver in re.findall(
                r'[\d\.]+[\d]*[\w]*',
                error_msg.split('(')[1].split(')')[0].split(':')[1]
            )
        ]
        try:
            return [v for v in versions if v.replace('.', '').isdigit()][-1]
        except IndexError:
            try:
                return versions[-1]
            except IndexError:
                return 'n/a'
