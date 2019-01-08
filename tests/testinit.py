import os
import shutil
from unittest import TestCase

from heliumcli import utils
from heliumcli.main import main

__author__ = "Alex Laird"
__copyright__ = "Copyright 2018, Helium Edu"
__version__ = "1.5.2"


class TestInitTestCase(TestCase):
    def setUp(self):
        self.build_dir = os.path.join("tests", "_build")
        if os.path.exists(self.build_dir):
            shutil.rmtree(self.build_dir)
            utils._config_cache = None
        os.mkdir(self.build_dir)

        os.environ["HELIUMCLI_CONFIG_PATH"] = os.path.join(self.build_dir, ".heliumcli.test.yml")

    def tearDown(self):
        shutil.rmtree(self.build_dir)
        utils._config_cache = None

    def test_init(self):
        # GIVEN
        self.assertFalse(os.path.exists(os.environ.get("HELIUMCLI_CONFIG_PATH")))

        # WHEN
        main(["main.py", "init", "my-project", "My Project", "myproject.heliumedu.com", "HeliumEdu"])

        # THEN
        self.assertTrue(os.path.exists(os.environ.get("HELIUMCLI_CONFIG_PATH")))
