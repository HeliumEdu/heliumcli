import os

from mock import mock

from heliumcli.cli import update, update_projects, set_build, deploy_build, start_servers, prep_code, build_release, \
    list_builds
from heliumcli.config import Config
from tests.helpers.commonhelper import given_config_exists
from .helpers import testcase, commonhelper

__author__ = "Alex Laird"
__copyright__ = "Copyright 2019, Helium Edu"
__version__ = "2.0.0"


class TestActionsTestCase(testcase.HeliumCLITestCase):
    def test_update(self):
        # WHEN
        self.runner.invoke(update)

        # THEN
        self.mock_subprocess_call.assert_called_once_with(["pip", "install", "--upgrade", "heliumcli"])

    @mock.patch("os.path.exists", return_value=False)
    def test_update_clone_projects(self, mock_path_exists):
        # GIVEN
        given_config_exists(self)

        # WHEN
        self.runner.invoke(update_projects)

        # THEN
        config = Config()
        self.assertEqual(self.mock_git_repo.clone_from.call_count, 2)
        self.mock_subprocess_call.assert_any_call(
            ["make", "install", "-C", os.path.join(config.get_projects_dir(), "platform")])
        self.mock_subprocess_call.assert_any_call(
            ["make", "install", "-C", os.path.join(config.get_projects_dir(), "frontend")])

    @mock.patch("os.path.exists", return_value=True)
    def test_update_projects(self, mock_path_exists):
        # GIVEN
        config = Config()
        config._save_config(os.environ.get("HELIUMCLI_CONFIG_PATH"), config.get_default_settings())

        # WHEN
        self.runner.invoke(update_projects)

        # THEN
        self.assertEqual(self.mock_git_repo.return_value.git.pull.call_count, 3)
        self.mock_subprocess_call.assert_any_call(
            ["make", "install", "-C", os.path.join(config.get_projects_dir(), "platform")])
        self.mock_subprocess_call.assert_any_call(
            ["make", "install", "-C", os.path.join(config.get_projects_dir(), "frontend")])

    @mock.patch("os.path.exists", return_value=True)
    def test_set_build(self, mock_path_exists):
        # GIVEN
        config = Config()
        config._save_config(os.environ.get("HELIUMCLI_CONFIG_PATH"), config.get_default_settings())

        # WHEN
        self.runner.invoke(set_build, ["1.2.3"])

        # THEN
        self.mock_git_repo.return_value.git.checkout.assert_has_calls([mock.call("1.2.3"), mock.call("1.2.3")])
        self.mock_subprocess_call.assert_any_call(
            ["make", "install", "-C", os.path.join(config.get_projects_dir(), "platform")])
        self.mock_subprocess_call.assert_any_call(
            ["make", "install", "-C", os.path.join(config.get_projects_dir(), "frontend")])

    def test_start_servers(self):
        # GIVEN
        commonhelper.given_runserver_exists("platform")

        # WHEN
        self.runner.invoke(start_servers)

        # THEN
        config = Config()
        self.mock_subprocess_popen.assert_called_once_with(
            os.path.join(config.get_projects_dir(), "platform", config.get_config(True)["serverBinFilename"]))

    def test_deploy_build(self):
        self.subprocess_popen.stop()

        # GIVEN
        commonhelper.given_hosts_file_exists()

        # WHEN
        self.runner.invoke(deploy_build, ["1.2.3", "devbox"])

        # THEN
        config = Config()
        self.assertEqual(self.mock_subprocess_call.call_count, 2)
        self.mock_subprocess_call.assert_any_call(
            ["ssh", "-t", "vagrant@heliumedu.test", config.get_config(True)["hostProvisionCommand"]])
        self.mock_subprocess_call.assert_any_call(
            ["ansible-playbook",
             "--inventory-file={}/hosts/devbox".format(config.get_ansible_dir()), "-v",
             "--extra-vars",
             "build_version=1.2.3",
             "{}/{}.yml".format(config.get_ansible_dir(), "devbox")])

        self.subprocess_popen.start()

    def test_deploy_build_code_limit_hosts(self):
        # GIVEN
        given_config_exists(self)

        # WHEN
        self.runner.invoke(deploy_build, ["1.2.3", "devbox", "--roles", "host1,host2"])

        # THEN
        config = Config()
        self.mock_subprocess_call.assert_called_once_with(
            ["ansible-playbook",
             "--inventory-file={}/hosts/devbox".format(config.get_ansible_dir()), "-v",
             "--extra-vars",
             "build_version=1.2.3",
             "--tags", "code",
             "--limit", "host1,host2",
             "{}/{}.yml".format(config.get_ansible_dir(), "devbox")])

    def test_deploy_build_all_tags(self):
        # GIVEN
        given_config_exists(self)

        # WHEN
        self.runner.invoke(deploy_build, ["1.2.3", "devbox", "--migrate", "--code", "--envvars", "--conf", "--ssl"])

        # THEN
        config = Config()
        self.mock_subprocess_call.assert_called_once_with(
            ["ansible-playbook",
             "--inventory-file={}/hosts/devbox".format(config.get_ansible_dir()), "-v",
             "--extra-vars",
             "build_version=1.2.3",
             "--tags", "code,migrate,envvars,conf,ssl",
             "{}/{}.yml".format(config.get_ansible_dir(), "devbox")])

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
        self.runner.invoke(prep_code)

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
        self.runner.invoke(build_release, ["1.2.3"])

        # THEN
        self.assertEqual(self.mock_git_repo.return_value.create_tag.call_count, 2)
        self.assertEqual(self.mock_git_repo.return_value.git.commit.call_count, 2)
        commonhelper.verify_versioned_file_updated(self, version_file_path, "1.2.3")
        commonhelper.verify_versioned_file_updated(self, package_file_path, "1.2.3")
        commonhelper.verify_versioned_file_updated(self, versioned_file_path, "1.2.3")

    def test_list_builds(self):
        # GIVEN
        given_config_exists(self)

        # WHEN
        self.runner.invoke(list_builds, ["1.2.3"])

    def test_build_release_fails_when_dirty(self):
        # GIVEN
        repo_instance = self.mock_git_repo.return_value
        repo_instance.is_dirty = mock.MagicMock(return_value=True)
        given_config_exists(self)

        # WHEN
        self.runner.invoke(build_release, ["1.2.3"])

        # THEN
        self.mock_git_repo.return_value.create_tag.assert_not_called()
        self.mock_git_repo.return_value.git.commit.assert_not_called()