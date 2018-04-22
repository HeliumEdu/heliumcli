import unittest

from mock import mock

from .helpers.stubs import repo_stub
from ..main import main

__author__ = 'Alex Laird'
__copyright__ = 'Copyright 2018, Helium Edu'
__version__ = '1.1.1'


class TestActionsTestCase(unittest.TestCase):
    @mock.patch('heliumcli.actions.update.utils.get_copyright_name', return_value='Helium Edu')
    @mock.patch('heliumcli.actions.update.git.Repo', return_value=repo_stub)
    @mock.patch('heliumcli.actions.update.subprocess.call')
    def test_update(self, mock_call, mock_repo, mock_copyright_name):
        main(['main.py', 'update'])

        self.assertTrue(mock_repo.called)
        self.assertTrue(mock_call.called)
