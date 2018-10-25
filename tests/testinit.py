import os

from tests.helpers.commonhelper import given_config_exists
from .helpers import testcase

__author__ = 'Alex Laird'
__copyright__ = 'Copyright 2018, Helium Edu'
__version__ = '1.4.0'


class TestActionsTestCase(testcase.HeliumCLITestCase):
    def test_init(self):
        # GIVEN
        self.assertFalse(os.path.exists(os.environ.get("HELIUMCLI_CONFIG_PATH")))

        # WHEN
        given_config_exists()

        # THEN
        self.assertTrue(os.path.exists(os.environ.get("HELIUMCLI_CONFIG_PATH")))
