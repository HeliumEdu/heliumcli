import os

import git

from .. import utils

__author__ = "Alex Laird"
__copyright__ = "Copyright 2019, Helium Edu"
__version__ = "2.0.0"


class ListBuildsAction:
    def run(self, args):
        config = utils.get_config()
        projects_dir = utils.get_projects_dir()

        if config["projectsRelativeDir"] != ".":
            root_dir = os.path.abspath(os.path.join(projects_dir, ".."))
            if os.path.exists(os.path.join(root_dir, ".git")):
                print(utils.get_repo_name(root_dir))

                repo = git.Repo(root_dir)
                repo.git.fetch(tags=True, prune=True)
                version_tags = utils.sort_tags(repo.tags)

                if len(version_tags) == 0:
                    print("No version tags have been created yet.")

                    return

                if args.latest:
                    print(version_tags[-1])
                else:
                    for tag in version_tags:
                        print(tag)

                print("")
