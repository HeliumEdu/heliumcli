import os
import subprocess

import git

from .. import utils

__author__ = "Alex Laird"
__copyright__ = "Copyright 2018, Helium Edu"
__version__ = "1.5.0"


class UpdateProjectsAction:
    def __init__(self):
        self.name = "update-projects"
        self.help = "Ensure all projects have the latest code and dependencies installed"

    def setup(self, subparsers):
        parser = subparsers.add_parser(self.name, help=self.help)
        parser.set_defaults(action=self)

    def run(self, args):
        config = utils.get_config()
        projects_dir = utils.get_projects_dir()

        if config["projectsRelativeDir"] != ".":
            root_dir = os.path.abspath(os.path.join(projects_dir, ".."))
            if os.path.exists(os.path.join(root_dir, ".git")):
                print(utils.get_repo_name(root_dir, config["remoteName"]))

                repo = git.Repo(root_dir)
                repo.git.fetch(tags=True, prune=True, force=os.environ.get("HELIUMCLI_FORCE_FETCH", "False") == "True")
                if os.environ.get("HELIUMCLI_SKIP_UPDATE_PULL", "False") != "True":
                    print(repo.git.pull() + "\n")

        if not os.path.exists(projects_dir):
            os.mkdir(projects_dir)

        for project in utils.get_projects(config):
            print(project)

            if config["projectsRelativeDir"] != ".":
                project_path = os.path.join(projects_dir, project)
            else:
                project_path = os.path.join(projects_dir)

            if not os.path.exists(os.path.join(project_path, ".git")):
                print("Cloning repo to ./projects/{}".format(project))
                git.Repo.clone_from("{}/{}.git".format(config["gitProject"], project), project_path)
            else:
                repo = git.Repo(project_path)
                repo.git.fetch(tags=True, prune=True, force=os.environ.get("HELIUMCLI_FORCE_FETCH", "False") == "True")
                print(repo.git.pull())

            subprocess.call(["make", "install", "-C", project_path])

            print("")
