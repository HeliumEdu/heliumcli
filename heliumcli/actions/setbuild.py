import os
import subprocess

import git

from .. import utils

__author__ = "Alex Laird"
__copyright__ = "Copyright 2018, Helium Edu"
__version__ = "1.5.0"


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
        projects_dir = utils.get_projects_dir()

        if config["projectsRelativeDir"] != ".":
            root_dir = os.path.abspath(os.path.join(projects_dir, ".."))
            if os.path.exists(os.path.join(root_dir, ".git")):
                print(utils.get_repo_name(root_dir, config["remoteName"]))

                repo = git.Repo(root_dir)
                repo.git.fetch(tags=True, prune=True)
                repo.git.checkout(args.version)

                print("")

        for project in utils.get_projects(config):
            print(project)

            if config["projectsRelativeDir"] != ".":
                project_path = os.path.join(projects_dir, project)
            else:
                project_path = os.path.join(projects_dir)

            repo = git.Repo(project_path)
            repo.git.fetch(tags=True, prune=True)
            repo.git.checkout(args.version)

            subprocess.call(["make", "install", "-C", project_path])

            print("")
