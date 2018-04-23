import os
import shutil
from unittest import TestCase

from git import TagReference
from mock import mock

from ...actions import utils

__author__ = 'Alex Laird'
__copyright__ = 'Copyright 2018, Helium Edu'
__version__ = '1.1.1'


class HeliumCLITestCase(TestCase):
    def setUp(self):
        self.build_dir = os.path.join(utils.get_heliumcli_dir(), "tests", "_build")
        if os.path.exists(self.build_dir):
            shutil.rmtree(self.build_dir)
            utils._config_cache = None
        os.mkdir(self.build_dir)

        os.environ["HELIUMCLI_CONFIG_FILENAME"] = os.path.join(self.build_dir, "config.test.yml")
        os.environ["HELIUMCLI_PROJECTS_RELATIVE_DIR"] = os.path.join("tests", "_build", "projects")
        os.environ["HELIUMCLI_ANSIBLE_RELATIVE_DIR"] = os.path.join("tests", "_build", "ansible")

        self._setup_git_mocks()

        self._setup_subprocess_mocks()

        self._setup_util_mocks()

    def tearDown(self):
        shutil.rmtree(self.build_dir)
        utils._config_cache = None

    def _setup_git_mocks(self):
        self.git_repo = mock.patch("git.Repo")
        self.addCleanup(self.git_repo.stop)
        self.mock_git_repo = self.git_repo.start()
        repo_instance = self.mock_git_repo.return_value
        repo_instance.create_tag = mock.MagicMock(return_value=TagReference("repo", "refs/tags/1.2.3"))
        repo_instance.git.pull = mock.MagicMock("git.cmd.Git", return_value="Already up to date.")
        repo_instance.git.fetch = mock.MagicMock("git.cmd.Git")
        repo_instance.git.add = mock.MagicMock("git.cmd.Git")
        repo_instance.git.checkout = mock.MagicMock("git.cmd.Git",
                                                    "Already on \"master\"\n"
                                                    "Your branch is up to date with \"origin/master\".")
        repo_instance.git.commit = mock.MagicMock("git.cmd.Git")
        repo_instance.git.commit = mock.MagicMock("git.cmd.Git")
        repo_instance.remotes["origin"].push = mock.MagicMock("git.cmd.Git")

    def _setup_subprocess_mocks(self):
        self.subprocess_call = mock.patch("subprocess.call")
        self.addCleanup(self.subprocess_call.stop)
        self.mock_subprocess_call = self.subprocess_call.start()

        self.subprocess_popen = mock.patch("subprocess.Popen")
        self.addCleanup(self.subprocess_popen.stop)
        self.mock_subprocess_popen = self.subprocess_popen.start()

    def _setup_util_mocks(self):
        self.utils_get_copyright_name = mock.patch("heliumcli.actions.utils.get_copyright_name",
                                                   return_value="Helium Edu")
        self.addCleanup(self.utils_get_copyright_name.stop)
        self.mock_get_copyright_name = self.utils_get_copyright_name.start()

        self.utils_get_repo_name = mock.patch("heliumcli.actions.utils.get_repo_name", return_value="deploy")
        self.addCleanup(self.utils_get_repo_name.stop)
        self.mock_get_repo_name = self.utils_get_repo_name.start()
