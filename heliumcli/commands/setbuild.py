import os
import subprocess

import click
import git

__author__ = "Alex Laird"
__copyright__ = "Copyright 2019, Helium Edu"
__version__ = "2.0.0"


class SetBuildCommand:
    def __init__(self, ctx, version):
        self.ctx = ctx
        self.version = version

    def run(self):
        config = self.ctx.config.get_config()
        projects_dir = self.ctx.config.get_projects_dir()

        if config["projectsRelativeDir"] != ".":
            root_dir = os.path.abspath(os.path.join(projects_dir, ".."))
            if os.path.exists(os.path.join(root_dir, ".git")):
                click.echo(self.ctx.config.get_repo_name(root_dir))

                repo = git.Repo(root_dir)
                repo.git.fetch(tags=True, prune=True)
                repo.git.checkout(self.version)

                click.echo("")

        for project in self.ctx.config.get_projects(config):
            click.echo(project)

            if config["projectsRelativeDir"] != ".":
                project_path = os.path.join(projects_dir, project)
            else:
                project_path = os.path.join(projects_dir)

            repo = git.Repo(project_path)
            repo.git.fetch(tags=True, prune=True)
            repo.git.checkout(self.version)

            subprocess.call(["make", "install", "-C", project_path])

            click.echo("")
