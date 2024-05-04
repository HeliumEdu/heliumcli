__copyright__ = "Copyright (c) 2018 Helium Edu"
__license__ = "MIT"

import os
import sys
from unittest import mock
from unittest.mock import patch

from heliumcli import settings, utils
from heliumcli.cli import main
from tests.helpers.commonhelper import given_config_exists
from .helpers import commonhelper, testcase


class TestActionsTestCase(testcase.HeliumCLITestCase):
    def test_update(self):
        # WHEN
        with patch.object(sys, "argv", ["cli.py", "update"]):
            main()

        # THEN
        self.mock_subprocess_call.assert_called_once_with(["pip", "install", "--upgrade", "heliumcli"])

    @mock.patch("os.path.exists", return_value=False)
    def test_update_clone_projects(self, mock_path_exists):
        # GIVEN
        given_config_exists()

        # WHEN
        with patch.object(sys, "argv", ["cli.py", "update-projects"]):
            main()

        # THEN
        self.assertEqual(self.mock_git_repo.clone_from.call_count, 2)
        self.mock_subprocess_call.assert_any_call(
            ["make", "install", "-C", os.path.join(utils.get_projects_dir(), "platform")])
        self.mock_subprocess_call.assert_any_call(
            ["make", "install", "-C", os.path.join(utils.get_projects_dir(), "frontend")])

    @mock.patch("os.path.exists", return_value=True)
    def test_update_projects(self, mock_path_exists):
        # GIVEN
        utils._save_config(os.environ.get("HELIUMCLI_CONFIG_PATH"), settings.get_default_settings())

        # WHEN
        with patch.object(sys, "argv", ["cli.py", "update-projects"]):
            main()

        # THEN
        self.assertEqual(self.mock_git_repo.return_value.git.pull.call_count, 3)
        self.mock_subprocess_call.assert_any_call(
            ["make", "install", "-C", os.path.join(utils.get_projects_dir(), "platform")])
        self.mock_subprocess_call.assert_any_call(
            ["make", "install", "-C", os.path.join(utils.get_projects_dir(), "frontend")])

    @mock.patch("os.path.exists", return_value=True)
    def test_set_build(self, mock_path_exists):
        # GIVEN
        utils._save_config(os.environ.get("HELIUMCLI_CONFIG_PATH"), settings.get_default_settings())

        # WHEN
        with patch.object(sys, "argv", ["cli.py", "set-build", "1.2.3"]):
            main()

        # THEN
        self.mock_git_repo.return_value.git.checkout.assert_has_calls([mock.call("1.2.3"), mock.call("1.2.3")])
        self.mock_subprocess_call.assert_any_call(
            ["make", "install", "-C", os.path.join(utils.get_projects_dir(), "platform")])
        self.mock_subprocess_call.assert_any_call(
            ["make", "install", "-C", os.path.join(utils.get_projects_dir(), "frontend")])

    def test_start_servers(self):
        # GIVEN
        commonhelper.given_runserver_exists("platform")

        # WHEN
        with patch.object(sys, "argv", ["cli.py", "start-servers"]):
            main()

        # THEN
        self.mock_subprocess_popen.assert_called_once_with(
            os.path.join(utils.get_projects_dir(), "platform", utils.get_config(True)["serverBinFilename"]))

    def test_deploy_build(self):
        self.subprocess_popen.stop()

        # GIVEN
        commonhelper.given_hosts_file_exists()

        # WHEN
        with patch.object(sys, "argv", ["cli.py", "deploy-build", "1.2.3", "devbox"]):
            main()

        # THEN
        self.assertEqual(self.mock_subprocess_call.call_count, 2)
        self.mock_subprocess_call.assert_any_call(
            ["ssh", "-t", "vagrant@heliumedu.test", utils.get_config(True)["hostProvisionCommand"]])
        self.mock_subprocess_call.assert_any_call(
            ["ansible-playbook",
             f"--inventory-file={utils.get_ansible_dir()}/hosts/devbox", "-v",
             "--extra-vars",
             "build_version=1.2.3",
             f"{utils.get_ansible_dir()}/devbox.yml"])

        self.subprocess_popen.start()

    def test_deploy_build_code_limit_hosts(self):
        # GIVEN
        given_config_exists()

        # WHEN
        with patch.object(sys, "argv",
                          ["cli.py", "deploy-build", "1.2.3", "devbox", "--code", "--roles", "host1,host2"]):
            main()

        # THEN
        self.mock_subprocess_call.assert_called_once_with(
            ["ansible-playbook",
             f"--inventory-file={utils.get_ansible_dir()}/hosts/devbox", "-v",
             "--extra-vars",
             "build_version=1.2.3",
             "--tags", "code",
             "--limit", "host1,host2",
             f"{utils.get_ansible_dir()}/devbox.yml"])

    def test_deploy_build_all_tags(self):
        # GIVEN
        given_config_exists()

        # WHEN
        with patch.object(sys, "argv",
                          ["cli.py", "deploy-build", "1.2.3", "devbox", "--code", "--migrate", "--envvars", "--conf",
                           "--ssl"]):
            main()

        # THEN
        self.mock_subprocess_call.assert_called_once_with(
            ["ansible-playbook",
             f"--inventory-file={utils.get_ansible_dir()}/hosts/devbox", "-v",
             "--extra-vars",
             "build_version=1.2.3",
             "--tags", "code,migrate,envvars,conf,ssl",
             f"{utils.get_ansible_dir()}/devbox.yml"])

    def test_prep_code(self):
        # GIVEN
        commonhelper.given_python_version_file_exists("1.2.3")
        versioned_file1_path = commonhelper.given_project_python_versioned_file_exists("platform")
        versioned_file2_path = commonhelper.given_project_js_versioned_file_exists("frontend")
        repo_instance = self.mock_git_repo.return_value
        latest_tag = repo_instance.tags[-1]
        latest_tag.commit = mock.MagicMock("git.commit.Commit")
        diff1 = mock.MagicMock("git.diff.Diff")
        diff1.b_rawpath = versioned_file1_path.encode("utf-8")
        diff2 = mock.MagicMock("git.diff.Diff")
        diff2.b_rawpath = versioned_file2_path.encode("utf-8")
        latest_tag.commit.diff = mock.MagicMock(side_effect=[[diff1], [diff2]])

        # WHEN
        with patch.object(sys, "argv", ["cli.py", "prep-code"]):
            main()

        # THEN
        commonhelper.verify_versioned_file_updated(self, versioned_file1_path, "1.2.3")
        commonhelper.verify_versioned_file_updated(self, versioned_file2_path, "1.2.3")

    def test_build_release(self):
        # GIVEN
        version_file_path = commonhelper.given_python_version_file_exists()
        package_file_path = commonhelper.given_project_package_json_exists("frontend")
        versioned_file_path = commonhelper.given_project_python_versioned_file_exists("platform")
        repo_instance = self.mock_git_repo.return_value
        repo_instance.untracked_files = []
        repo_instance.is_dirty = mock.MagicMock(side_effect=[False, False, True, True])
        latest_tag = repo_instance.tags[-1]
        latest_tag.commit = mock.MagicMock("git.commit.Commit")
        diff1 = mock.MagicMock("git.diff.Diff")
        diff1.b_rawpath = versioned_file_path.encode("utf-8")
        latest_tag.commit.diff = mock.MagicMock(side_effect=[[diff1], []])

        # WHEN
        with patch.object(sys, "argv", ["cli.py", "build-release", "1.2.3"]):
            main()

        # THEN
        self.assertEqual(self.mock_git_repo.return_value.create_tag.call_count, 2)
        self.assertEqual(self.mock_git_repo.return_value.git.commit.call_count, 2)
        commonhelper.verify_versioned_file_updated(self, version_file_path, "1.2.3")
        commonhelper.verify_versioned_file_updated(self, package_file_path, "1.2.3")
        commonhelper.verify_versioned_file_updated(self, versioned_file_path, "1.2.3")

    def test_list_builds(self):
        # GIVEN
        given_config_exists()

        # WHEN
        with patch.object(sys, "argv", ["cli.py", "--silent", "list-builds"]):
            main()

    def test_build_release_fails_when_dirty(self):
        # GIVEN
        repo_instance = self.mock_git_repo.return_value
        repo_instance.is_dirty = mock.MagicMock(return_value=True)
        given_config_exists()

        # WHEN
        with patch.object(sys, "argv", ["cli.py", "build-release", "1.2.3"]):
            try:
                main()
            except SystemExit:
                self.assertTrue(True)

        # THEN
        self.mock_git_repo.return_value.create_tag.assert_not_called()
        self.mock_git_repo.return_value.git.commit.assert_not_called()
