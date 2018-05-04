import os

from mock import mock

from .helpers import testcase, commonhelper
from ..actions import utils
from ..main import main

__author__ = 'Alex Laird'
__copyright__ = 'Copyright 2018, Helium Edu'
__version__ = '1.1.3'


class TestActionsTestCase(testcase.HeliumCLITestCase):
    def test_update(self):
        # WHEN
        main(["main.py", "update"])

        # THEN
        self.mock_git_repo.return_value.git.pull.assert_called_once()
        self.mock_subprocess_call.assert_called_once_with(
            ["pip", "install", "-r", os.path.join(utils.get_heliumcli_dir(), "requirements.txt")])

    @mock.patch("os.path.exists", return_value=False)
    def test_update_clone_projects(self, mock_path_exists):
        # WHEN
        main(["main.py", "update-projects"])

        # THEN
        self.assertEqual(self.mock_git_repo.clone_from.call_count, 2)
        self.mock_subprocess_call.assert_any_call(
            ["make", "install", "-C", os.path.join(utils.get_projects_dir(), "platform")])
        self.mock_subprocess_call.assert_any_call(
            ["make", "install", "-C", os.path.join(utils.get_projects_dir(), "frontend")])

    @mock.patch("os.path.exists", return_value=True)
    def test_update_projects(self, mock_path_exists):
        # GIVEN
        utils._save_config(os.environ.get("HELIUMCLI_CONFIG_FILENAME"), utils._get_config_defaults())

        # WHEN
        main(["main.py", "update-projects"])

        # THEN
        self.assertEqual(self.mock_git_repo.return_value.git.pull.call_count, 3)
        self.mock_subprocess_call.assert_any_call(
            ["make", "install", "-C", os.path.join(utils.get_projects_dir(), "platform")])
        self.mock_subprocess_call.assert_any_call(
            ["make", "install", "-C", os.path.join(utils.get_projects_dir(), "frontend")])

    @mock.patch("os.path.exists", return_value=True)
    def test_set_build(self, mock_path_exists):
        # GIVEN
        utils._save_config(os.environ.get("HELIUMCLI_CONFIG_FILENAME"), utils._get_config_defaults())

        # WHEN
        main(["main.py", "set-build", "1.2.3"])

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
        main(["main.py", "start-servers"])

        # THEN
        self.mock_subprocess_popen.assert_called_once_with(
            os.path.join(utils.get_projects_dir(), "platform", utils.get_config()["serverBinFilename"]))

    def test_deploy_build(self):
        # GIVEN
        commonhelper.given_hosts_file_exists()

        # WHEN
        main(["main.py", "deploy-build", "1.2.3", "devbox"])

        # THEN
        self.assertEqual(self.mock_subprocess_call.call_count, 2)
        self.mock_subprocess_call.assert_any_call(
            ["ssh", "-t", "vagrant@heliumedu.test", utils.get_config()["hostProvisionCommand"]])
        self.mock_subprocess_call.assert_any_call(
            ["ansible-playbook",
             '--inventory-file={}/{}'.format(utils.get_ansible_dir(), utils.get_config()["ansibleHostsFilename"]), '-v',
             '--extra-vars',
             '"build_version=1.2.3"',
             '{}/{}.yml'.format(utils.get_ansible_dir(), "devbox")])

    def test_deploy_build_code_limit_hosts(self):
        # WHEN
        main(["main.py", "deploy-build", "1.2.3", "devbox", "--code", "--hosts", "host1,host2"])

        # THEN
        self.mock_subprocess_call.assert_called_once_with(
            ["ansible-playbook",
             '--inventory-file={}/{}'.format(utils.get_ansible_dir(), utils.get_config()["ansibleHostsFilename"]), '-v',
             '--extra-vars',
             '"build_version=1.2.3"',
             '--tags', '"code"',
             '--limit', '"host1,host2"',
             '{}/{}.yml'.format(utils.get_ansible_dir(), "devbox")])

    def test_deploy_build_all_tags(self):
        # WHEN
        main(["main.py", "deploy-build", "1.2.3", "devbox", "--code", "--migrate", "--envvars", "--conf", "--ssl"])

        # THEN
        self.mock_subprocess_call.assert_called_once_with(
            ["ansible-playbook",
             '--inventory-file={}/{}'.format(utils.get_ansible_dir(), utils.get_config()["ansibleHostsFilename"]), '-v',
             '--extra-vars',
             '"build_version=1.2.3"',
             '--tags', '"code,migrate,envvars,conf,ssl"',
             '{}/{}.yml'.format(utils.get_ansible_dir(), "devbox")])

    def test_prep_code(self):
        # GIVEN
        commonhelper.given_python_version_file_exists("1.2.3")
        versioned_file1_path = commonhelper.given_project_python_versioned_file_exists("platform")
        versioned_file2_path = commonhelper.given_project_js_versioned_file_exists("frontend")
        repo_instance = self.mock_git_repo.return_value
        latest_tag = repo_instance.tags[-1]
        latest_tag.commit = mock.MagicMock('git.commit.Commit')
        diff1 = mock.MagicMock('git.diff.Diff')
        diff1.b_rawpath = versioned_file1_path.encode('utf-8')
        diff2 = mock.MagicMock('git.diff.Diff')
        diff2.b_rawpath = versioned_file2_path.encode('utf-8')
        latest_tag.commit.diff = mock.Mock(side_effect=[[diff1], [diff2]])

        # WHEN
        main(["main.py", "prep-code"])

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
        repo_instance.is_dirty = mock.Mock(side_effect=[False, False, True, True])
        latest_tag = repo_instance.tags[-1]
        latest_tag.commit = mock.MagicMock('git.commit.Commit')
        diff1 = mock.MagicMock('git.diff.Diff')
        diff1.b_rawpath = versioned_file_path.encode('utf-8')
        latest_tag.commit.diff = mock.Mock(side_effect=[[diff1], []])

        # WHEN
        main(["main.py", "build-release", "1.2.3"])

        # THEN
        self.assertEqual(self.mock_git_repo.return_value.create_tag.call_count, 2)
        self.assertEqual(self.mock_git_repo.return_value.git.commit.call_count, 2)
        commonhelper.verify_versioned_file_updated(self, version_file_path, "1.2.3")
        commonhelper.verify_versioned_file_updated(self, package_file_path, "1.2.3")
        commonhelper.verify_versioned_file_updated(self, versioned_file_path, "1.2.3")

    def test_build_release_fails_when_dirty(self):
        # GIVEN
        repo_instance = self.mock_git_repo.return_value
        repo_instance.is_dirty = mock.MagicMock(return_value=True)

        # WHEN
        main(["main.py", "build-release", "1.2.3"])

        # THEN
        self.mock_git_repo.return_value.create_tag.assert_not_called()
        self.mock_git_repo.return_value.git.commit.assert_not_called()
