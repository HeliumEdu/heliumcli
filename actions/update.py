import os
import subprocess

from . import utils

__author__ = 'Alex Laird'
__copyright__ = 'Copyright 2018, Helium Edu'
__version__ = '1.1.0'


class UpdateAction:
    def __init__(self):
        self.name = "update"
        self.help = "Update the CLI tool to the latest version"

    def setup(self, subparsers):
        parser = subparsers.add_parser(self.name, help=self.help)
        parser.set_defaults(action=self)

    def run(self, args):
        subprocess.call(["git", "-C", utils.get_heliumcli_dir(), "pull"])
        subprocess.call(["pip", "install", "-r", os.path.join(utils.get_heliumcli_dir(), "requirements.txt")])
