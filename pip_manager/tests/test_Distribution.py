# -*- coding: utf-8 -*-
from __future__ import print_function
import sys

from pip_manager.distribution import Distribution

import pytest


class TestDistribution(object):
    @pytest.fixture(autouse=True)
    def init(self, mocker):
        self.mocked_pip = mocker.patch('pip_manager.distribution.pip')
        self.dist = Distribution(name='foo', version='9.99.999')

    def test_instance_creation(self, mocker):
        mocked_get_newest_version = mocker.patch(
            'pip_manager.distribution.Distribution.get_newest_version'
        )
        mocked_get_newest_version.return_value = '10.11.111'
        d = Distribution(name='foo', version='9.99.999')
        assert d.name == 'foo'
        assert d.version == '9.99.999'
        assert d.newest_version == '10.11.111'
        assert not d.is_selected
        assert mocked_get_newest_version.called

    @pytest.mark.parametrize(
        'err_str, expected', [
            ('fake error msg (1.22.333)\n with continuation line', '1.22.333'),
            ('fake error msg (1.22.333)', '1.22.333'),
            ('fake error msg 1.22.333 ee', '1.22.333'),
            ('fake error msg (1.22.333) end', '1.22.333'),
            ('fake error msg (1.22.333)end', '1.22.333'),
            ('fake error msg (1.22.b333)end', '1.22.b333'),
            ('fake error msg (1.22) end', '1.22'),
            ('fake error msg (1) end', '1'),
            ('fake error msg () end', 'n/a'),
            ('', 'n/a'),
        ]
    )
    def test_get_newest_version(self, err_str, expected):
        self.mocked_pip.main = lambda _: print(err_str, file=sys.stderr)
        assert self.dist.get_newest_version() == expected
