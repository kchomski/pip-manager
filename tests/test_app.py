# -*- coding: utf-8 -*-
import sys
from collections import namedtuple
import pytest

from pip_manager.app import PipManager


def test_init(mocker):
    mocked_Gui = mocker.patch('pip_manager.app.Gui')
    mocker.patch('pip_manager.app.PipManager.get_distributions')

    pm = PipManager()

    assert pm.page == 0
    assert pm.cursor_pos == 0
    mocked_Gui.assert_called_with(line_width=79)
    assert pm.get_distributions.called


@pytest.fixture
def pm(mocker):
    mocker.patch('pip_manager.app.Gui')
    mocker.patch('pip_manager.app.Distribution.get_newest_version').return_value = '9.99.999'
    mocked_pkg_resources = mocker.patch('pip_manager.app.pkg_resources')
    DummyWorkingSetDist = namedtuple('DummyWorkingSetDist', ['key', 'version'])
    mocked_working_set = mocker.PropertyMock(return_value=[
        DummyWorkingSetDist(key='pip', version='9.0.3'),
        DummyWorkingSetDist(key='flask', version='1.0.0'),
        DummyWorkingSetDist(key='pytest', version='3.5.0'),
    ])
    type(mocked_pkg_resources).working_set = mocked_working_set
    return PipManager()


Distribution = namedtuple('Distribution', ['name', 'version'])


@pytest.mark.parametrize('page, win_height, expected', [
    (0, 0, []),
    (0, 1, [Distribution(name='flask', version='1.0.0')]),
    (1, 1, [Distribution(name='pip', version='9.0.3')]),
    (2, 1, [Distribution(name='pytest', version='3.5.0')]),
    (0, 2, [Distribution(name='flask', version='1.0.0'), Distribution(name='pip', version='9.0.3')]),
    (1, 2, [Distribution(name='pytest', version='3.5.0')]),
    (0, 3, [Distribution(name='flask', version='1.0.0'), Distribution(name='pip', version='9.0.3'), Distribution(name='pytest', version='3.5.0')]),
])
def test_dists_to_draw(page, win_height, expected, pm):
    pm.page = page
    pm.gui.dist_win_height = win_height
    assert pm.dists_to_draw == expected


def test_get_distributions(pm):
    assert pm.get_distributions() == [
        Distribution(name='flask', version='1.0.0'),
        Distribution(name='pip', version='9.0.3'),
        Distribution(name='pytest', version='3.5.0'),
    ]
    assert pm.gui.draw_popup.called


def test_toggle_one(pm):
    assert pm.distributions[0].is_selected is False
    pm.toggle_one(0)
    assert pm.distributions[0].is_selected
    pm.toggle_one(0)
    assert pm.distributions[0].is_selected is False


def test_toggle_all(pm):
    assert all(not d.is_selected for d in pm.distributions)
    pm.toggle_all()
    assert all(d.is_selected for d in pm.distributions)
    pm.toggle_all()
    assert all(not d.is_selected for d in pm.distributions)

    pm.distributions[0].is_selected = True
    pm.toggle_all()
    assert all(d.is_selected for d in pm.distributions)


def test_update_distributions(mocker, pm):
    mocked_subprocess = mocker.patch('pip_manager.app.subprocess')
    pm.distributions[0].is_selected = True

    pm.update_distributions()

    mocked_subprocess.call.assert_called_with([sys.executable, '-m', 'pip', 'install', '-U', 'flask'], stdout=mocker.ANY, stderr=mocker.ANY)
    assert pm.distributions[0].is_selected is False
    assert pm.distributions[0].version == '9.99.999'


def test_update_distributions_none_selected(mocker, pm):
    mocked_subprocess = mocker.patch('pip_manager.app.subprocess')

    pm.update_distributions()

    assert not mocked_subprocess.call.called
    assert pm.distributions[0].is_selected is False
    assert pm.distributions[0].version == '1.0.0'


def test_update_distributions_no_newest_version(mocker, pm):
    mocked_subprocess = mocker.patch('pip_manager.app.subprocess')
    pm.distributions[0].is_selected = True
    pm.distributions[0].newest_version = 'n/a'

    pm.update_distributions()

    assert not mocked_subprocess.call.called
    assert pm.distributions[0].is_selected
    assert pm.distributions[0].version == '1.0.0'


def test_update_distributions_same_versions(mocker, pm):
    mocked_subprocess = mocker.patch('pip_manager.app.subprocess')
    pm.distributions[0].is_selected = True
    pm.distributions[0].newest_version = '1.0.0'

    pm.update_distributions()

    assert not mocked_subprocess.call.called
    assert pm.distributions[0].is_selected
    assert pm.distributions[0].version == '1.0.0'


def test_uninstall_distributions(mocker, pm):
    mocked_subprocess = mocker.patch('pip_manager.app.subprocess')
    mocked_get_protected_dists = mocker.patch('pip_manager.app.get_protected_dists')
    mocked_get_protected_dists.return_value = ['pip']
    pm.gui.stdscr.getch.return_value = ord('y')

    pm.distributions[0].is_selected = True

    pm.uninstall_distributions()

    assert mocked_subprocess.call.called
    assert not any(d.name == 'flask' for d in pm.distributions)
    assert len(pm.distributions) == 2


def test_uninstall_distributions_none_selected(mocker, pm):
    mocked_subprocess = mocker.patch('pip_manager.app.subprocess')
    mocked_get_protected_dists = mocker.patch('pip_manager.app.get_protected_dists')
    mocked_get_protected_dists.return_value = ['pip']

    pm.uninstall_distributions()

    assert not mocked_subprocess.call.called
    assert len(pm.distributions) == 3


def test_uninstall_distributions_protected(mocker, pm):
    mocked_subprocess = mocker.patch('pip_manager.app.subprocess')
    mocked_get_protected_dists = mocker.patch('pip_manager.app.get_protected_dists')
    mocked_get_protected_dists.return_value = ['pip']

    pm.distributions[1].is_selected = True

    pm.uninstall_distributions()

    assert not mocked_subprocess.call.called
    assert len(pm.distributions) == 3


def test_uninstall_distributions_non_confirmed(mocker, pm):
    mocked_subprocess = mocker.patch('pip_manager.app.subprocess')
    mocked_get_protected_dists = mocker.patch('pip_manager.app.get_protected_dists')
    mocked_get_protected_dists.return_value = ['pip']
    pm.gui.stdscr.getch.return_value = ord('n')

    pm.distributions[0].is_selected = True

    pm.uninstall_distributions()

    assert not mocked_subprocess.call.called
    assert len(pm.distributions) == 3


@pytest.mark.parametrize('dist_win_height, expected', [
    (1, 2),
    (2, 1),
    (3, 0),
])
def test_last_page(dist_win_height, expected, pm):
    pm.gui.dist_win_height = dist_win_height
    assert pm.last_page == expected
