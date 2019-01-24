import os
import shutil
from unittest import TestCase

from click.testing import CliRunner

from heliumcli.cli import init

__author__ = "Alex Laird"
__copyright__ = "Copyright 2019, Helium Edu"
__version__ = "2.0.0"


class TestInitTestCase(TestCase):
    def setUp(self):
        self.runner = CliRunner()

        self.build_dir = os.path.join("tests", "_build")
        if os.path.exists(self.build_dir):
            shutil.rmtree(self.build_dir)
        os.mkdir(self.build_dir)

        os.environ["HELIUMCLI_CONFIG_PATH"] = os.path.join(self.build_dir, ".heliumcli.test.yml")

    def tearDown(self):
        shutil.rmtree(self.build_dir)

    def test_init(self):
        # GIVEN
        self.assertFalse(os.path.exists(os.environ.get("HELIUMCLI_CONFIG_PATH")))

        # WHEN
        self.runner.invoke(init, ["my-project", "My Project", "myproject.heliumedu.com", "HeliumEdu"])

        # THEN
        self.assertTrue(os.path.exists(os.environ.get("HELIUMCLI_CONFIG_PATH")))
