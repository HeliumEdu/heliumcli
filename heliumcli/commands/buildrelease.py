import datetime
import os
import shutil

import click
import git

from .prepcode import PrepCodeCommand

__author__ = "Alex Laird"
__copyright__ = "Copyright 2019, Helium Edu"
__version__ = "2.0.0"


class BuildReleaseCommand:
    def __init__(self, ctx, version, roles):
        self.ctx = ctx
        self.version = version
        self.roles = roles

    def run(self):
        config = self.ctx.config.get_config()
        projects_dir = self.ctx.config.get_projects_dir()

        # First ensure all repos are in a clean state with all changes committed
        dirty_repos = []
        for project in self.ctx.config.get_projects(config):
            if self.roles and project not in self.roles:
                continue

            if config["projectsRelativeDir"] != ".":
                project_path = os.path.join(projects_dir, project)
            else:
                project_path = os.path.join(projects_dir)

            repo = git.Repo(project_path)

            if repo.untracked_files or repo.is_dirty():
                dirty_repos.append(project)
            else:
                repo.git.fetch(tags=True, prune=True)
                repo.git.checkout("master")

        if len(dirty_repos) > 0:
            click.echo(
                "WARN: this operation cannot be performed when a repo is dirty. Commit all changes to the following "
                "repos before proceeding: {}".format(dirty_repos))

            return

        version = self.version.lstrip("v")

        self._update_version_file(version,
                                  os.path.join(config["versionInfo"]["project"], config["versionInfo"]["path"]))

        prep_code_command = PrepCodeCommand(self.ctx, self.roles)
        prep_code_command.run()

        click.echo("Committing changes and creating release tags ...")

        for project in self.ctx.config.get_projects(config):
            click.echo(project)

            if config["projectsRelativeDir"] != ".":
                project_path = os.path.join(projects_dir, project)
            else:
                project_path = os.path.join(projects_dir)

            self._commit_and_tag(project_path, version)

        if config["projectsRelativeDir"] != ".":
            root_dir = os.path.abspath(os.path.join(projects_dir, ".."))
            if os.path.exists(os.path.join(root_dir, ".git")):
                click.echo(self.ctx.config.get_repo_name(root_dir))
                self._commit_and_tag(root_dir, version)

        click.echo("... release version {} built.".format(version))

    def _commit_and_tag(self, path, version):
        repo = git.Repo(path)

        if version in repo.tags:
            click.echo("Version already exists, not doing anything.")
        else:
            if repo.is_dirty():
                repo.git.add(u=True)
                repo.git.commit(m="[heliumcli] Release {}".format(version))
                repo.remotes["origin"].push("master")
            tag = repo.create_tag(version, m="")
            repo.remotes["origin"].push(tag)

    def _update_version_file(self, version, path):
        config = self.ctx.config.get_config()

        version_file_path = os.path.join(self.ctx.config.get_projects_dir(), path)

        version_file = open(version_file_path, "r")
        new_version_file = open(version_file_path + ".tmp", "w")

        for line in version_file:
            if version_file_path.endswith(".py"):
                if line.strip().startswith("__version__ ="):
                    line = "__version__ = \"{}\"\n".format(version)
                elif line.strip().startswith("__copyright__ = "):
                    line = "__copyright__ = \"Copyright {}, {}\"\n".format(str(datetime.date.today().year),
                                                                           self.ctx.config.get_copyright_name())
            elif version_file.name == "package.json":
                if line.strip().startswith("\"version\":"):
                    line = "  \"version\": \"{}\",\n".format(version)
            # TODO: implement other known types
            else:
                click.echo(
                    "WARN: helium-cli does not know how to process this type of file for version file: {}".format(
                        config["versionInfo"]["path"]))

                new_version_file.close()
                os.remove(version_file_path + ".tmp")

                return

            new_version_file.write(line)

        version_file.close()
        new_version_file.close()

        shutil.copy(version_file_path + ".tmp", version_file_path)
        os.remove(version_file_path + ".tmp")
