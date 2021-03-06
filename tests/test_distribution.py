# -*- coding: utf-8 -*-
import sys
from subprocess import CalledProcessError
from subprocess import STDOUT

import pytest

from pip_manager.distribution import Distribution


@pytest.fixture(autouse=True)
def mocked_get_newest_version(request, mocker):
    if 'dont_use_mocked_get_newest_version' in request.keywords:
        return
    mocker.patch('pip_manager.distribution.Distribution.get_newest_version').return_value = '9.99.999'


def test_init():
    d = Distribution(name='flask', version='1.0.0')

    assert d.name == 'flask'
    assert d.version == '1.0.0'
    assert d.newest_version == '9.99.999'
    assert d.is_selected is False
    assert d.get_newest_version.called


@pytest.mark.parametrize('name1, ver1, name2, ver2, expected', [
    ('flask', '1.0.0', 'flask', '1.0.0', True),
    ('flask', '1.0.0', 'flask', '1.0.1', False),
    ('flask', '1.0.0', 'flaskk', '1.0.0', False),
    ('flask', '1.0.0', 'flaskk', '1.0.1', False),
])
def test_eq(name1, ver1, name2, ver2, expected):
    assert (Distribution(name=name1, version=ver1) == Distribution(name=name2, version=ver2)) is expected


@pytest.mark.dont_use_mocked_get_newest_version
@pytest.mark.parametrize('name, versions, expected', [
    ('pip', '10.0.0b2, 10.0.0, 10.0.1', '10.0.1'),
    ('pip', '10.0.0b2, 10.0.0, 10.0.1, 10.0.2a', '10.0.1'),
    ('pip', '10.0.0b2', '10.0.0b2'),
    ('pip', '', 'n/a'),
])
def test_get_newest_version(name, versions, expected, mocker):
    mocked_subprocess = mocker.patch('pip_manager.distribution.subprocess')
    mocked_subprocess.check_output.side_effect = CalledProcessError(
        returncode=1,
        cmd='dummy cmd',
        output=(
            'ERROR: Could not find a version that satisfies the requirement {0}==lxPhr_ffmS3fZ3E4P7U1Lw '
            '(from versions: {1})\nERROR: No matching distribution found for {0}==lxPhr_ffmS3fZ3E4P7U1Lw\n'.format(name, versions)
        ).encode(),
    )
    d = Distribution(name=name, version='1.0.0')
    assert d.newest_version == expected
    mocked_subprocess.check_output.assert_called_with([sys.executable, '-m', 'pip', 'install', '{}==lxPhr_ffmS3fZ3E4P7U1Lw'.format(name)], stderr=STDOUT)
