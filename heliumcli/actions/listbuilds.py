import os

import git

from .. import utils

__author__ = "Alex Laird"
__copyright__ = "Copyright 2018, Helium Edu"
__version__ = "1.5.0"


class ListBuildsAction:
    def __init__(self):
        self.name = "list-builds"
        self.help = "List available builds"

    def setup(self, subparsers):
        parser = subparsers.add_parser(self.name, help=self.help)
        parser.add_argument("--latest", action="store_true", help="Only list the latest build")
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
