import os
import shutil
from unittest import TestCase

from git import TagReference
from mock import mock

from heliumcli import utils

__author__ = 'Alex Laird'
__copyright__ = 'Copyright 2018, Helium Edu'
__version__ = '1.1.7'


class HeliumCLITestCase(TestCase):
    def setUp(self):
        self.build_dir = os.path.join("tests", "_build")
        if os.path.exists(self.build_dir):
            shutil.rmtree(self.build_dir)
            utils._config_cache = None
        os.mkdir(self.build_dir)

        os.environ["HELIUMCLI_CONFIG_PATH"] = os.path.join(self.build_dir, ".heliumcli.test.yml")
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

        repo_instance.git.pull = mock.MagicMock("git.cmd.Git", return_value="Already up to date.")
        repo_instance.git.fetch = mock.MagicMock("git.cmd.Git")
        repo_instance.git.add = mock.MagicMock("git.cmd.Git")
        repo_instance.git.checkout = mock.MagicMock("git.cmd.Git",
                                                    "Already on \"master\"\n"
                                                    "Your branch is up to date with \"origin/master\".")
        repo_instance.git.commit = mock.MagicMock("git.cmd.Git")
        repo_instance.git.commit = mock.MagicMock("git.cmd.Git")
        repo_instance.remotes["origin"].push = mock.MagicMock("git.cmd.Git")

        repo_instance.create_tag = mock.MagicMock(return_value=TagReference(repo_instance, "refs/tags/1.2.3"))
        tag1 = mock.MagicMock('git.tag.TagReference')
        tag1.tag = mock.MagicMock('git.tag.TagObject')
        tag1.tag.tag = "1.2.0"
        tag2 = mock.MagicMock('git.tag.TagReference')
        tag2.tag = mock.MagicMock('git.tag.TagObject')
        tag2.tag.tag = "1.2.1"
        tag3 = mock.MagicMock('git.tag.TagReference')
        tag3.tag = mock.MagicMock('git.tag.TagObject')
        tag3.tag.tag = "1.2.2"
        repo_instance.tags = [tag1, tag2, tag3]

    def _setup_subprocess_mocks(self):
        self.subprocess_call = mock.patch("subprocess.call")
        self.addCleanup(self.subprocess_call.stop)
        self.mock_subprocess_call = self.subprocess_call.start()

        self.subprocess_popen = mock.patch("subprocess.Popen")
        self.addCleanup(self.subprocess_popen.stop)
        self.mock_subprocess_popen = self.subprocess_popen.start()

    def _setup_util_mocks(self):
        self.utils_get_copyright_name = mock.patch("heliumcli.utils.get_copyright_name",
                                                   return_value="Helium Edu")
        self.addCleanup(self.utils_get_copyright_name.stop)
        self.mock_get_copyright_name = self.utils_get_copyright_name.start()

        self.utils_get_repo_name = mock.patch("heliumcli.utils.get_repo_name", return_value="deploy")
        self.addCleanup(self.utils_get_repo_name.stop)
        self.mock_get_repo_name = self.utils_get_repo_name.start()
