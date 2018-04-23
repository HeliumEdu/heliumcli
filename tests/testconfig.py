import os

from mock import mock

from .helpers import testcase
from ..actions import utils

__author__ = 'Alex Laird'
__copyright__ = 'Copyright 2018, Helium Edu'
__version__ = '1.1.1'


class TestActionsTestCase(testcase.HeliumCLITestCase):
    def test_default_config_created(self):
        # GIVEN
        self.assertFalse(os.path.exists(os.environ.get("HELIUMCLI_CONFIG_FILENAME")))

        # WHEN
        utils.get_config()

        # THEN
        self.assertTrue(os.environ.get("HELIUMCLI_CONFIG_FILENAME"))

    @mock.patch("os.path.exists", return_value=True)
    def test_config_already_exists(self, mock_path_exists):
        # GIVEN
        utils._create_default_config(os.environ.get("HELIUMCLI_CONFIG_FILENAME"))
        utils.get_config()
        mock_path_exists.reset_mock()

        # WHEN
        utils.get_config()

        # THEN
        mock_path_exists.assert_not_called()

    def test_custom_config_created(self):
        # GIVEN
        self.assertFalse(os.path.exists(os.environ.get("HELIUMCLI_CONFIG_FILENAME")))
        os.environ["HELIUMCLI_GIT_PROJECT"] = "git@example.com:SomeProject"
        os.environ["HELIUMCLI_PROJECTS"] = '["proj1", "proj2", "project3"]'
        os.environ["HELIUMCLI_PROJECTS_RELATIVE_DIR"] = "some/dir/projects"
        os.environ["HELIUMCLI_SERVER_BIN_FILENAME"] = "some/bin/server"
        os.environ["HELIUMCLI_ANSIBLE_RELATIVE_DIR"] = "some/dir/ansible"
        os.environ["HELIUMCLI_ANSIBLE_HOSTS_FILENAME"] = "myhosts"
        os.environ["HELIUMCLI_ANSIBLE_COPYRIGHT_NAME_VAR"] = "my_dev_name"
        os.environ["HELIUMCLI_VERSION_INFO_PROJECT"] = "proj2"
        os.environ["HELIUMCLI_VERSION_INFO_PATH"] = "some/path/project/version"

        # WHEN
        config = utils.get_config()

        # THEN
        self.assertTrue(os.environ.get("HELIUMCLI_CONFIG_FILENAME"))
        self.assertEqual(config, {
            "ansibleCopyrightNameVar": "my_dev_name",
            "ansibleHostsFilename": "myhosts",
            "ansibleRelativeDir": "some/dir/ansible",
            "gitProject": "git@example.com:SomeProject",
            "projects": ["proj1", "proj2", "project3"],
            "projectsRelativeDir": "some/dir/projects",
            "serverBinFilename": "some/bin/server",
            "versionInfo": {"path": "some/path/project/version", "project": "proj2"}
        })
