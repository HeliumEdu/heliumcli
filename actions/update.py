import os
import subprocess

import git

from . import utils

__author__ = 'Alex Laird'
__copyright__ = 'Copyright 2018, Helium Edu'
__version__ = '1.1.2'


class UpdateAction:
    def __init__(self):
        self.name = "update"
        self.help = "Update the CLI tool to the latest version"

    def setup(self, subparsers):
        parser = subparsers.add_parser(self.name, help=self.help)
        parser.set_defaults(action=self)

    def run(self, args):
        repo = git.Repo(utils.get_heliumcli_dir())

        repo.git.fetch(tags=True, prune=True)
        print(repo.git.pull() + "\n")

        subprocess.call(["pip", "install", "-r", os.path.join(utils.get_heliumcli_dir(), "requirements.txt")])
