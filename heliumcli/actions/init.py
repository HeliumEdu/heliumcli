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
        parser.add_argument("id", help="The ID (no spaces) to give to the new project")
        parser.add_argument("name", help="The friendly name to give to the new project")
        parser.add_argument("host", help="The hostname to give the project")
        parser.add_argument("github-user", help="The GitHub username or project name")
        parser.set_defaults(action=self)

    def run(self, args):
        config_path = os.path.abspath(os.environ.get("HELIUMCLI_CONFIG_PATH", ".heliumcli.yml"))
        if os.path.exists(config_path):
            print("It looks like a helium-cli project already exists in this directory, not doing anything.")

            sys.exit(1)

        utils.get_config(True)

        self._init_project(args)

        print("A new helium-cli project has been initialized.")

    def _init_project(self, args):
        # TODO: implement template init
        pass
