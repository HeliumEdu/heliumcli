import os

import click
import git

from .. import utils

__author__ = "Alex Laird"
__copyright__ = "Copyright 2019, Helium Edu"
__version__ = "2.0.0"


class ListBuildsCommand:
    def __init__(self, ctx, latest):
        self.ctx = ctx
        self.latest = latest

    def run(self):
        config = self.ctx.config.get_config()
        projects_dir = self.ctx.config.get_projects_dir()

        if config["projectsRelativeDir"] != ".":
            root_dir = os.path.abspath(os.path.join(projects_dir, ".."))
            if os.path.exists(os.path.join(root_dir, ".git")):
                click.echo(self.ctx.config.get_repo_name(root_dir))

                repo = git.Repo(root_dir)
                repo.git.fetch(tags=True, prune=True)
                version_tags = utils.sort_tags(repo.tags)

                if len(version_tags) == 0:
                    click.echo("No version tags have been created yet.")

                    return

                if self.latest:
                    click.echo(version_tags[-1])
                else:
                    for tag in version_tags:
                        click.echo(tag)

                click.echo("")
