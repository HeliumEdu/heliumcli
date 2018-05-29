import os
import subprocess

import git

from .. import utils

__author__ = 'Alex Laird'
__copyright__ = 'Copyright 2018, Helium Edu'
__version__ = '1.1.7'


class SetBuildAction:
    def __init__(self):
        self.name = "set-build"
        self.help = "Set all projects to the specified build, which may be a versioned release or a branch"

    def setup(self, subparsers):
        parser = subparsers.add_parser(self.name, help=self.help)
        parser.add_argument("version", help="The build version to be deployed, which may be a version or a branch")
        parser.set_defaults(action=self)

    def run(self, args):
        config = utils.get_config('init' in args)
        projects_dir = utils.get_projects_dir()

        root_dir = os.path.abspath(os.path.join(projects_dir, ".."))
        if os.path.exists(os.path.join(root_dir, ".git")):
            print(utils.get_repo_name(root_dir))

            repo = git.Repo(root_dir)
            repo.git.fetch(tags=True, prune=True)
            repo.git.checkout(args.version)

            print("")

        for project in config["projects"]:
            print(project)

            repo = git.Repo(os.path.join(projects_dir, project))
            repo.git.fetch(tags=True, prune=True)
            repo.git.checkout(args.version)

            subprocess.call(["make", "install", "-C", os.path.join(projects_dir, project)])

            print("")
