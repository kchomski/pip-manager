# -*- coding: utf-8 -*-
from pip_manager import app

from pip_manager.app import PipManager

import pytest


class Test_PipManager(object):

    @pytest.fixture(autouse=True)
    def custom_init(self, mocker):
        mocker.spy(app, 'Distribution')
        mocker.spy(app, 'get_protected_dists')
        mocker.patch('pip_manager.distribution.Distribution.get_newest_version').return_value = '9.99.999'
        mocker.patch('pip_manager.distribution.pip', autospec=True)

        self.mocked_pip = mocker.patch('pip_manager.app.pip', autospec=True)

        class FakePipDist(object):
            def __init__(self, key, version):
                self.key = key
                self.version = version

        self.mocked_pip.get_installed_distributions.return_value = [
            FakePipDist(key, version) for key, version in [
                ['alabaster', '0.7.10'],
                ['Babel', '2.4.0'],
                ['bleach', '2.0.0'],
                ['certifi', '2017.7.27.1'],
                ['chardet', '3.0.4'],
                ['decorator', '4.1.2'],
                ['Django', '1.11.4'],
                ['docutils', '0.14'],
                ['entrypoints', '0.2.3'],
                ['html5lib', '0.999999999'],
                ['idna', '2.6'],
                ['imagesize', '0.7.1'],
                ['ipykernel', '4.6.1'],
                ['ipyparallel', '6.0.2'],
                ['ipython', '6.1.0'],
                ['ipython-genutils', '0.2.0'],
                ['ipywidgets', '6.0.0'],
                ['itsdangerous', '0.24'],
                ['jedi', '0.10.2'],
                ['Jinja2', '2.9.6'],
                ['jsonschema', '2.6.0'],
                ['jupyter-client', '5.1.0'],
                ['jupyter-core', '4.3.0'],
                ['MarkupSafe', '1.0'],
                ['mistune', '0.7.4'],
                ['nbconvert', '5.2.1'],
                ['nbformat', '4.3.0'],
                ['nose', '1.3.7'],
                ['notebook', '5.0.0'],
                ['pandocfilters', '1.4.2'],
                ['pexpect', '4.2.1'],
                ['pickleshare', '0.7.4'],
                ['pip', '9.0.1'],
                ['prompt-toolkit', '1.0.15'],
                ['ptyprocess', '0.5.2'],
                ['py', '1.4.34'],
                ['Pygments', '2.2.0'],
                ['pytest', '3.2.1'],
                ['pytest-mock', '1.6.2'],
                ['pytest-runner', '2.11.1'],
                ['python-dateutil', '2.6.1'],
                ['pytz', '2017.2'],
                ['pyzmq', '16.0.2'],
                ['qtconsole', '4.3.0'],
                ['requests', '2.18.3'],
                ['setuptools', '36.2.7'],
                ['simplegeneric', '0.8.1'],
                ['six', '1.10.0'],
                ['snowballstemmer', '1.2.1'],
                ['Sphinx', '1.6.3'],
                ['sphinxcontrib-websupport', '1.0.1'],
                ['terminado', '0.6'],
                ['testpath', '0.3.1'],
                ['tornado', '4.5.1'],
                ['traitlets', '4.3.2'],
                ['urllib3', '1.22'],
                ['wcwidth', '0.1.7'],
                ['webencodings', '0.5.1'],
                ['Werkzeug', '0.12.2'],
                ['wheel', '0.29.0'],
                ['widgetsnbextension', '2.0.0'],
                ['yapf', '0.16.3']
            ]
        ]

        self.mocked_gui = mocker.patch('pip_manager.app.Gui', autospec=True)
        mocker.spy(PipManager, 'get_distributions')
        self.pm = PipManager()

    def test_initialization(self):
        self.mocked_gui.assert_called_with(79)
        assert self.pm.page == 0
        assert self.pm.cursor_pos == 0
        assert self.pm.get_distributions.called

    @pytest.mark.parametrize(
        'page, dist_win_height, start_idx, stop_idx',
        [
            (0, 17, 0, 17),
            (0, 20, 0, 20),
            (1, 20, 20, 40),
            (0, 100, 0, 100),
            (0, 100, 0, 80),
        ]

    )
    def test_dists_to_draw(self, page, dist_win_height, start_idx, stop_idx):
        self.pm.page = page
        self.pm.gui.dist_win_height = dist_win_height
        assert self.pm.dists_to_draw == self.pm.distributions[start_idx:stop_idx]

    def test_get_distributions(self):
        rv = self.pm.get_distributions()
        assert self.mocked_pip.get_installed_distributions.called
        assert self.pm.gui.draw_popup.called
        assert app.Distribution.called
        assert self.pm.distributions == rv

    def test_toggle_one(self):
        self.pm.toggle_one(0)
        assert self.pm.distributions[0].is_selected
        self.pm.toggle_one(0)
        assert not self.pm.distributions[0].is_selected

    def test_toggle_all(self):
        self.pm.toggle_all()
        assert all(d.is_selected for d in self.pm.distributions)
        self.pm.toggle_all()
        assert not any(d.is_selected for d in self.pm.distributions)

    def test_update_distributions(self):
        for d in self.pm.distributions[:5]:
            d.is_selected = True

        self.pm.update_distributions()
        assert self.pm.gui.draw_popup.called

        for d in self.pm.distributions[:5]:
            self.mocked_pip.main.assert_any_call(['install', '--upgrade', d.name])
            assert d.version == d.newest_version

        assert not any(d.is_selected for d in self.pm.distributions)

    def test_uninstall_distributions_decline(self):
        for d in self.pm.distributions[:5]:
            d.is_selected = True

        self.pm.gui.stdscr.getch.return_value = ord('N')

        self.pm.uninstall_distributions()

        assert app.get_protected_dists.called
        assert not self.mocked_pip.main.called

        for d in self.pm.distributions[:5]:
            assert d.is_selected

    @pytest.mark.parametrize('accept_char', ['y', 'Y'])
    def test_uninstall_distributions_accept(self, accept_char):
        to_delete = self.pm.distributions[:5]

        for d in self.pm.distributions[:5]:
            d.is_selected = True

        self.pm.gui.stdscr.getch.return_value = ord(accept_char)

        self.pm.uninstall_distributions()

        assert app.get_protected_dists.called
        assert self.mocked_pip.main.called

        for d in to_delete:
            assert d not in self.pm.distributions

    def test_uninstall_distributions_protected(self, mocker):
        mocker.patch('pip_manager.app.get_protected_dists').return_value = ['pip', 'wheel']

        for d in self.pm.distributions:
            d.is_selected = True if d.name in ['pip', 'wheel'] else False

        self.pm.uninstall_distributions()

        assert app.get_protected_dists.called
        assert not self.pm.gui.stdscr.getch.called
        assert not self.mocked_pip.main.called

        assert any(d.name == 'pip' for d in self.pm.distributions)
        assert any(d.name == 'wheel' for d in self.pm.distributions)

    @pytest.mark.parametrize(
        'dist_win_height, expected',
        [
            (100, 0),
            (50, 1),
            (30, 2),
            (17, 3),
            (15, 4),
            (10, 6),
            (5, 12),
            (1, 61),
        ]
    )
    def test_last_page(self, dist_win_height, expected):
        self.pm.gui.dist_win_height = dist_win_height
        assert self.pm.last_page == expected
