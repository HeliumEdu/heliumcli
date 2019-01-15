import os
import sys

import click

from heliumcli.config import Config

__author__ = "Alex Laird"
__copyright__ = "Copyright 2019, Helium Edu"
__version__ = "2.0.0"

CMD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "commands"))
CONTEXT_SETTINGS = dict(auto_envvar_prefix="HELIUMCLI", help_option_names=["-h", "--help"])


class Context(object):
    def __init__(self):
        self.verbose = False
        self.config = Config()

    def log(self, msg, *args):
        """Logs a message to stderr."""
        if args:
            msg %= args
        click.echo(msg, file=sys.stderr)

    def vlog(self, msg, *args):
        """Logs a message to stderr if verbose is enabled."""
        if self.verbose:
            self.log(msg, *args)


pass_context = click.make_pass_decorator(Context, ensure=True)


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__)
@pass_context
def cli(ctx):
    """CLI that provides a useful set of tools for maintaining, building, and deploying code in compatible projects."""
    pass


@click.command()
@click.argument("version")
@click.option("--roles", help="Limit the project roles to be built/tagged")
@pass_context
def build_release(ctx):
    """Build a release version for all projects, tagging when complete"""
    pass


@click.command()
@click.argument("version")
@click.argument("env")
@click.option("--roles", help="Limit the project roles to be deployed")
@click.option("--migrate", help="Install code dependencies and run migrations")
@click.option("--code", help="Only deploy code")
@click.option("--envvars", help="Only deploy environment variables")
@click.option("--conf", help="Only deploy configuration files and restart necessary services")
@click.option("--ssl", help="Only deploy SSL certificates and restart necessary services")
@pass_context
def deploy_build(ctx):
    """Deploy the specified build, which may be a versioned release or a branch"""
    pass


@click.command()
@click.argument("id")
@click.argument("name")
@click.argument("host")
@click.argument("github_user")
@click.option("--config-only", help="Only initialize the .heliumcli.yml config file")
@pass_context
def init(ctx):
    """Initialize a new project with an that is compatible with helium-cli, providing an ID (slug with no spaces),
    friendly name, hostname for the webservice, and GitHub username"""
    pass


@click.command()
@click.option("--latest", help="Only list the latest build")
@pass_context
def list_builds(ctx):
    """List available builds"""
    pass


@click.command()
@click.option("--roles", help="Limit the project roles to be prepped")
@pass_context
def prep_code(ctx):
    """Prepare code for release build, updating version and copyright information in project files"""
    pass


@click.command()
@click.argument("version")
@pass_context
def set_build(ctx):
    """Set all projects to the specified build, which may be a versioned release or a branch"""
    pass


@click.command()
@pass_context
def start_servers(ctx):
    """Launch known project servers to run locally"""
    pass


@click.command()
@pass_context
def update(ctx):
    """Update the CLI tool to the latest version"""
    pass


@click.command()
@pass_context
def update_projects(ctx):
    """Ensure all projects have the latest code and dependencies"""
    pass


cli.add_command(build_release)
cli.add_command(deploy_build)
cli.add_command(init)
cli.add_command(list_builds)
cli.add_command(prep_code)
cli.add_command(set_build)
cli.add_command(start_servers)
cli.add_command(update)
cli.add_command(update_projects)

if __name__ == '__main__':
    cli()
