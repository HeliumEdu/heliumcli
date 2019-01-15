import os
import subprocess

import click
import git

__author__ = "Alex Laird"
__copyright__ = "Copyright 2019, Helium Edu"
__version__ = "2.0.0"


class UpdateProjectsCommand:
    def __init__(self, ctx):
        self.ctx = ctx

    def run(self):
        config = self.ctx.config.get_config()
        projects_dir = self.ctx.config.get_projects_dir()

        if config["projectsRelativeDir"] != ".":
            root_dir = os.path.abspath(os.path.join(projects_dir, ".."))
            if os.path.exists(os.path.join(root_dir, ".git")):
                click.echo(self.ctx.config.get_repo_name(root_dir))

                repo = git.Repo(root_dir)
                repo.git.fetch(tags=True, prune=True)
                click.echo(repo.git.pull() + "\n")

        if not os.path.exists(projects_dir):
            os.mkdir(projects_dir)

        for project in self.ctx.config.get_projects(config):
            click.echo(project)

            if config["projectsRelativeDir"] != ".":
                project_path = os.path.join(projects_dir, project)
            else:
                project_path = os.path.join(projects_dir)

            if not os.path.exists(os.path.join(project_path, ".git")):
                click.echo("Cloning repo to ./projects/{}".format(project))
                git.Repo.clone_from("{}/{}.git".format(config["gitProject"], project), project_path)
            else:
                repo = git.Repo(project_path)
                repo.git.fetch(tags=True, prune=True)
                click.echo(repo.git.pull())

            subprocess.call(["make", "install", "-C", project_path])

            click.echo("")
