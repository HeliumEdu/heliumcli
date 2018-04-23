import os

from mock import mock

from .helpers import testcase, commonhelper
from ..actions import utils
from ..main import main

__author__ = 'Alex Laird'
__copyright__ = 'Copyright 2018, Helium Edu'
__version__ = '1.1.1'


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
        utils._create_default_config(os.environ.get("HELIUMCLI_CONFIG_FILENAME"))

        # WHEN
        main(["main.py", "update-projects"])

        # THEN
        self.assertEqual(self.mock_git_repo.return_value.git.pull.call_count, 3)
        self.mock_subprocess_call.assert_any_call(
            ["make", "install", "-C", os.path.join(utils.get_projects_dir(), "platform")])
        self.mock_subprocess_call.assert_any_call(
            ["make", "install", "-C", os.path.join(utils.get_projects_dir(), "frontend")])

    def test_set_build(self):
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
            os.path.join(utils.get_projects_dir(), "platform", utils.get_config()["serverBinFilename"]), shell=True)

    def test_deploy_build(self):
        # WHEN
        main(["main.py", "deploy-build", "1.2.3", "devbox"])

        # THEN
        self.mock_subprocess_call.assert_any_call(
            'ansible-playbook --inventory-file={}/{} -v {}/{}.yml --extra-vars "build_version={}"'.format(
                utils.get_ansible_dir(),
                utils.get_config()["ansibleHostsFilename"],
                utils.get_ansible_dir(),
                "devbox",
                "1.2.3"), shell=True)

    def test_deploy_build_code_limit_hosts(self):
        # WHEN
        main(["main.py", "deploy-build", "1.2.3", "devbox", "--code", "--hosts", "host1,host2"])

        # THEN
        self.mock_subprocess_call.assert_any_call(
            'ansible-playbook --inventory-file={}/{} -v {}/{}.yml --extra-vars "build_version={}" --tags "{}" --limit "{}"'.format(
                utils.get_ansible_dir(),
                utils.get_config()["ansibleHostsFilename"],
                utils.get_ansible_dir(),
                "devbox",
                "1.2.3",
                "code",
                "host1,host2"), shell=True)

    def test_deploy_build_all_tags(self):
        # GIVEN
        commonhelper.given_hosts_file_exists()

        # WHEN
        main(["main.py", "deploy-build", "1.2.3", "devbox", "--code", "--migrate", "--envvars", "--conf", "--ssl"])

        # THEN
        self.mock_subprocess_call.assert_any_call(
            'ansible-playbook --inventory-file={}/{} -v {}/{}.yml --extra-vars "build_version={}" --tags "{}"'.format(
                utils.get_ansible_dir(),
                utils.get_config()["ansibleHostsFilename"],
                utils.get_ansible_dir(),
                "devbox",
                "1.2.3",
                "code,migrate,envvars,conf,ssl"), shell=True)
