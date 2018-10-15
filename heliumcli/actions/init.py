import os

import sys

from .. import utils

__author__ = 'Alex Laird'
__copyright__ = 'Copyright 2018, Helium Edu'
__version__ = '1.4.0'


class InitAction:
    def __init__(self):
        self.name = "init"
        self.help = "Initialize a new project that is compatible with helium-cli"

    def setup(self, subparsers):
        parser = subparsers.add_parser(self.name, help=self.help)
        parser.add_argument("--template-project", action="store_true", help="Initialize a project from a template Django project")
        parser.set_defaults(action=self)

    def run(self, args):
        config_path = os.path.abspath(os.environ.get("HELIUMCLI_CONFIG_PATH", ".heliumcli.yml"))
        if os.path.exists(config_path):
            print("It looks like a helium-cli project already exists in this directory, not doing anything.")

            sys.exit(1)

        utils.get_config(True)

        # TODO: implement template-project config

        print("A new helium-cli project has been initialized.")
