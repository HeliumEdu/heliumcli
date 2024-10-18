__copyright__ = "Copyright (c) 2018 Helium Edu"
__license__ = "MIT"

import datetime
import git
import os
import shutil
import sys

from .prepcode import PrepCodeAction
from .. import utils


class BuildReleaseAction:
    def __init__(self):
        self.name = "build-release"
        self.help = "Build a release version for all projects, tagging when complete"

    def setup(self, subparsers):
        parser = subparsers.add_parser(self.name, help=self.help)
        parser.add_argument("version", help="The version number to be tagged")
        parser.add_argument("--roles", action="store", type=str, nargs="*",
                            help="Limit the project roles to be built/tagged")
        parser.set_defaults(action=self)

    def run(self, args):
        config = utils.get_config()
        projects_dir = utils.get_projects_dir()

        # First ensure all repos are in a clean state with all changes committed
        dirty_repos = []
        for project in utils.get_projects(config):
            if args.roles and project not in args.roles:
                continue

            if config["projectsRelativeDir"] != ".":
                project_path = os.path.join(projects_dir, project)
            else:
                project_path = os.path.join(projects_dir)

            repo = git.Repo(project_path)

            if repo.untracked_files or repo.is_dirty():
                print(f"Untracked files in {project}: {repo.untracked_files}")

                dirty_repos.append(project)
            else:
                repo.git.fetch(tags=True, prune=True)
                repo.git.checkout(config["branchName"])

        if len(dirty_repos) > 0:
            print(
                f"Error: this operation cannot be performed when a repo is dirty. Commit all "
                f"changes to the following repos before proceeding: {dirty_repos}")

            sys.exit(1)

        version = args.version.lstrip("v")

        self._update_version_file(version,
                                  os.path.join(config["versionInfo"]["project"],
                                               config["versionInfo"]["path"]))

        prepcodeaction = PrepCodeAction()
        prepcodeaction.run(args)

        print("Committing changes and creating release tags ...")

        for project in utils.get_projects(config):
            print(project)

            if config["projectsRelativeDir"] != ".":
                project_path = os.path.join(projects_dir, project)
            else:
                project_path = os.path.join(projects_dir)

            self._commit_and_tag(project_path, version, config["remoteName"], config["branchName"])

        if config["projectsRelativeDir"] != "." and config["tagRootRelease"]:
            root_dir = os.path.abspath(os.path.join(projects_dir, ".."))
            if os.path.exists(os.path.join(root_dir, ".git")):
                print(utils.get_repo_name(root_dir, config["remoteName"]))
                self._commit_and_tag(root_dir, version, config["remoteName"], config["branchName"])

        print(f"... release version {version} built.")

    def _commit_and_tag(self, path, version, remote_name, branch_name):
        repo = git.Repo(path)

        if version in repo.tags:
            print("Version already exists, not doing anything.")
        else:
            if repo.is_dirty():
                repo.git.add(u=True)
                repo.git.commit(m=f"[heliumcli] Release {version}")
                repo.remotes[remote_name].push(branch_name)
            tag = repo.create_tag(version, m="")
            repo.remotes[remote_name].push(tag)

    def _update_version_file(self, version, path):
        config = utils.get_config()

        version_file_path = os.path.join(utils.get_projects_dir(), path)

        version_file = open(version_file_path, "r")
        new_version_file = open(version_file_path + ".tmp", "w")

        for line in version_file:
            if version_file_path.endswith(".py"):
                if line.strip().startswith("__version__ ="):
                    line = f"__version__ = \"{version}\"\n"
                elif utils.get_config()["updateCopyrightYear"] and \
                        line.strip().startswith("__copyright__ = "):
                    line = "__copyright__ = \"Copyright (c) {year}, {name}\"\n".format(
                        year=str(datetime.date.today().year), name=utils.get_copyright_name())
            elif version_file.name == "package.json":
                if line.strip().startswith("\"version\":"):
                    line = f"  \"version\": \"{version}\",\n"
            # TODO: implement other known types
            else:
                print("WARN: helium-cli does not know how to process this type of file for "
                      "version file: {path}".format(path=config["versionInfo"]["path"]))

                new_version_file.close()
                os.remove(version_file_path + ".tmp")

                return

            new_version_file.write(line)

        version_file.close()
        new_version_file.close()

        shutil.copy(version_file_path + ".tmp", version_file_path)
        os.remove(version_file_path + ".tmp")
