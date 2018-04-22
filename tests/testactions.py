import os

from mock import mock

from .helpers.testcase import HeliumCLITestCase
from ..actions import utils
from ..main import main

__author__ = 'Alex Laird'
__copyright__ = 'Copyright 2018, Helium Edu'
__version__ = '1.1.1'


class TestActionsTestCase(HeliumCLITestCase):
    def test_update(self):
        main(['main.py', 'update'])

        self.mock_git_repo.return_value.git.pull.assert_called_once()
        self.mock_subprocess_call.assert_called_once_with(
            ['pip', 'install', '-r', os.path.join(utils.get_heliumcli_dir(), "requirements.txt")])

    def test_update_clone_projects(self):
        main(['main.py', 'update-projects'])

        self.assertEqual(self.mock_git_repo.clone_from.call_count, 2)
        self.mock_subprocess_call.assert_any_call(
            ['make', 'install', '-C', os.path.join(utils.get_projects_dir(), "platform")])
        self.mock_subprocess_call.assert_any_call(
            ['make', 'install', '-C', os.path.join(utils.get_projects_dir(), "frontend")])

    @mock.patch('os.path.exists', return_value=True)
    def test_update_projects(self, mock_path_exists):
        main(['main.py', 'update-projects'])

        self.assertEqual(self.mock_git_repo.return_value.git.pull.call_count, 3)
        self.mock_subprocess_call.assert_any_call(
            ['make', 'install', '-C', os.path.join(utils.get_projects_dir(), "platform")])
        self.mock_subprocess_call.assert_any_call(
            ['make', 'install', '-C', os.path.join(utils.get_projects_dir(), "frontend")])
