import os
from unittest import mock

from heliumcli import utils, settings
from .helpers import testcase

__author__ = "Alex Laird"
__copyright__ = "Copyright 2018, Helium Edu"
__version__ = "1.6.0"


class TestConfigTestCase(testcase.HeliumCLITestCase):
    def test_default_config_created(self):
        # GIVEN
        self.assertFalse(os.path.exists(os.environ.get("HELIUMCLI_CONFIG_PATH")))

        # WHEN
        utils.get_config(True)

        # THEN
        self.assertTrue(os.path.exists(os.environ.get("HELIUMCLI_CONFIG_PATH")))

    @mock.patch("os.path.exists", return_value=True)
    def test_config_already_exists(self, mock_path_exists):
        # GIVEN
        utils._save_config(os.environ.get("HELIUMCLI_CONFIG_PATH"), settings.get_default_settings())
        utils.get_config(True)
        mock_path_exists.reset_mock()

        # WHEN
        utils.get_config(True)

        # THEN
        mock_path_exists.assert_not_called()

    def test_custom_config_created(self):
        # GIVEN
        self.assertFalse(os.path.exists(os.environ.get("HELIUMCLI_CONFIG_PATH")))
        os.environ["HELIUMCLI_GIT_PROJECT"] = "git@example.com:SomeProject"
        os.environ["HELIUMCLI_PROJECTS"] = "[\"proj1\", \"proj2\", \"project3\"]"
        os.environ["HELIUMCLI_PROJECTS_RELATIVE_DIR"] = "some/dir/projects"
        os.environ["HELIUMCLI_SERVER_BIN_FILENAME"] = "some/bin/server"
        os.environ["HELIUMCLI_ANSIBLE_RELATIVE_DIR"] = "some/dir/ansible"
        os.environ["HELIUMCLI_ANSIBLE_HOSTS_FILENAME"] = "myhosts"
        os.environ["HELIUMCLI_ANSIBLE_COPYRIGHT_NAME_VAR"] = "my_dev_name"
        os.environ["HELIUMCLI_VERSION_INFO_PROJECT"] = "proj2"
        os.environ["HELIUMCLI_VERSION_INFO_PATH"] = "some/path/project/version"
        os.environ["HELIUMCLI_HOST_PROVISION_COMMAND"] = "sudo yum install python"
        os.environ["HELIUMCLI_BRANCH_NAME"] = "fancy-main"
        os.environ["HELIUMCLI_REMOTE_NAME"] = "fancy-origin"

        # WHEN
        config = utils.get_config(True)

        # THEN
        self.assertTrue(os.environ.get("HELIUMCLI_CONFIG_PATH"))
        self.assertEqual(config, {
            "ansibleCopyrightNameVar": "my_dev_name",
            "ansibleRelativeDir": "some/dir/ansible",
            "gitProject": "git@example.com:SomeProject",
            "hostProvisionCommand": "sudo yum install python",
            "projects": ["proj1", "proj2", "project3"],
            "projectsRelativeDir": "some/dir/projects",
            "serverBinFilename": "some/bin/server",
            "versionInfo": {"path": "some/path/project/version", "project": "proj2"},
            "branchName": "fancy-main",
            "remoteName": "fancy-origin"
        })
