import os
import subprocess

import git

from .. import utils

__author__ = "Alex Laird"
__copyright__ = "Copyright 2019, Helium Edu"
__version__ = "2.0.0"


class SetBuildAction:
    def run(self, args):
        config = utils.get_config()
        projects_dir = utils.get_projects_dir()

        if config["projectsRelativeDir"] != ".":
            root_dir = os.path.abspath(os.path.join(projects_dir, ".."))
            if os.path.exists(os.path.join(root_dir, ".git")):
                print(utils.get_repo_name(root_dir))

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
