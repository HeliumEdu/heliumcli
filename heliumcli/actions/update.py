__copyright__ = "Copyright (c) 2018 Helium Edu"
__license__ = "MIT"

import subprocess


class UpdateAction:
    def __init__(self):
        self.name = "update"
        self.help = "Update the CLI tool to the latest version"

    def setup(self, subparsers):
        parser = subparsers.add_parser(self.name, help=self.help)
        parser.set_defaults(action=self)

    def run(self, args):
        subprocess.call(["pip", "install", "--upgrade", "heliumcli"])
