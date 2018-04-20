import git
import subprocess

import os

from . import utils

__author__ = 'Alex Laird'
__copyright__ = 'Copyright 2018, Helium Edu'
__version__ = '1.1.0'


class UpdateProjectsAction:
    def __init__(self):
        self.name = "update-projects"
        self.help = "Ensure all projects have the latest code and dependencies installed"

    def setup(self, subparsers):
        parser = subparsers.add_parser(self.name, help=self.help)
        parser.set_defaults(action=self)

    def run(self, args):
        config = utils.get_config()
        root_dir = utils.get_deploy_root_dir()
        projects_dir = os.path.join(root_dir, "projects")

        repo = git.Repo(root_dir)

        print(os.path.basename(root_dir))
        repo.git.fetch(tags=True, prune=True)
        print(repo.git.pull() + "\n")

        if not os.path.exists(projects_dir):
            os.mkdir(projects_dir)

        for project in config["projects"]:
            print(project)

            project_path = os.path.join(projects_dir, project)

            if not os.path.exists(os.path.join(project_path, ".git")):
                print("Cloning repo to ./projects/{}".format(project))
                git.Repo.clone_from("{}/{}.git".format(config["gitProject"], project), project_path)
            else:
                repo = git.Repo(project_path)
                repo.git.fetch(tags=True, prune=True)
                print(repo.git.pull())

            subprocess.call(["make", "install", "-C", os.path.join(root_dir, "projects", project)])

            print("")