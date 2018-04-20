import os
import subprocess

import git

from . import utils

__author__ = 'Alex Laird'
__copyright__ = 'Copyright 2018, Helium Edu'
__version__ = '1.1.0'


class SetBuildAction:
    def __init__(self):
        self.name = "set-build"
        self.help = "Set all projects to the specified build, which may be a versioned release or a branch"

    def setup(self, subparsers):
        parser = subparsers.add_parser(self.name, help=self.help)
        parser.add_argument("version", help="The build version to be deployed, which may be a version or a branch")
        parser.set_defaults(action=self)

    def run(self, args):
        config = utils.get_config()
        root_dir = utils.get_deploy_root_dir()
        projects_dir = os.path.join(root_dir, "projects")

        for project in config["projects"]:
            print(project)

            repo = git.Repo(os.path.join(projects_dir, project))
            repo.git.checkout(args.version)

            subprocess.call(["make", "install", "-C", os.path.join(root_dir, "projects", project)])

            print("")
