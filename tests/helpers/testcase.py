from unittest import TestCase

from mock import mock


class HeliumCLITestCase(TestCase):
    def setUp(self):
        self.utils_get_copyright_name = mock.patch("heliumcli.actions.utils.get_copyright_name",
                                                   return_value="Helium Edu")
        self.addCleanup(self.utils_get_copyright_name.stop)
        self.mock_get_copyright_name = self.utils_get_copyright_name.start()

        self.utils_get_repo_name = mock.patch("heliumcli.actions.utils.get_repo_name", return_value="deploy")
        self.addCleanup(self.utils_get_repo_name.stop)
        self.mock_get_repo_name = self.utils_get_repo_name.start()

        self.git_repo = mock.patch("git.Repo")
        self.addCleanup(self.git_repo.stop)
        self.mock_git_repo = self.git_repo.start()
        instance = self.mock_git_repo.return_value
        instance.git.pull = mock.MagicMock("git.cmd.Git", return_value="Already up to date.")
        instance.git.fetch = mock.MagicMock("git.cmd.Git")
        instance.git.add = mock.MagicMock("git.cmd.Git")
        instance.git.checkout = mock.MagicMock("git.cmd.Git",
                                               "Already on \"master\"\n"
                                               "Your branch is up to date with \"origin/master\".")
        instance.git.commit = mock.MagicMock("git.cmd.Git")

        self.subprocess_call = mock.patch("subprocess.call")
        self.addCleanup(self.subprocess_call.stop)
        self.mock_subprocess_call = self.subprocess_call.start()

        self.subprocess_popen = mock.patch("subprocess.Popen")
        self.addCleanup(self.subprocess_popen.stop)
        self.mock_subprocess_popen = self.subprocess_popen.start()
