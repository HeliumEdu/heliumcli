__copyright__ = "Copyright (c) 2018 Helium Edu"
__license__ = "MIT"

import os
import shutil
import sys
from unittest import TestCase
from unittest.mock import patch

from heliumcli import utils
from heliumcli.cli import main
from tests.helpers.testcase import TEST_BUILD_DIR


class TestInitTestCase(TestCase):
    def setUp(self):
        if os.path.exists(TEST_BUILD_DIR):
            shutil.rmtree(TEST_BUILD_DIR)
            utils._config_cache = None
        os.mkdir(TEST_BUILD_DIR)

        os.environ["HELIUMCLI_CONFIG_PATH"] = os.path.join(TEST_BUILD_DIR, ".heliumcli.test.yml")

    def tearDown(self):
        shutil.rmtree(TEST_BUILD_DIR)
        utils._config_cache = None

    def test_init(self):
        # GIVEN
        self.assertFalse(os.path.exists(os.environ.get("HELIUMCLI_CONFIG_PATH")))

        # WHEN
        with patch.object(sys, "argv",
                          ["cli.py", "init", "my-project", "My Project", "myproject.heliumedu.com", "HeliumEdu"]):
            main()

        # THEN
        self.assertTrue(os.path.exists(os.environ.get("HELIUMCLI_CONFIG_PATH")))
