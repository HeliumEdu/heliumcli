import os
import sys

import click

from heliumcli.config import Config

__author__ = "Alex Laird"
__copyright__ = "Copyright 2018, Helium Edu"
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


class HeliumCLI(click.MultiCommand):
    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(CMD_FOLDER):
            if filename == "__init__.py":
                continue

            if filename.endswith(".py"):
                rv.append(filename[:-3].replace('_', '-'))
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        if sys.version_info[0] == 2:
            name = name.encode("ascii", "replace")
        mod = __import__("heliumcli.commands.{}".format(name.replace('-', '_')), None, None, ["cli"])
        return mod.cli


@click.group(cli=HeliumCLI, context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__)
@click.option("-v", "--verbose", is_flag=True, help="Enables verbose mode.")
@pass_context
def cli(ctx, verbose):
    """CLI that provides a useful set of tools for maintaining, building, and deploying code in compatible projects."""
    ctx.verbose = verbose

    # actions = {
    #     InitAction(),
    #     UpdateAction(),
    #     UpdateProjectsAction(),
    #     SetBuildAction(),
    #     StartServersAction(),
    #     PrepCodeAction(),
    #     BuildReleaseAction(),
    #     DeployBuildAction(),
    #     ListBuildsAction(),
    # }
    #
    # parser = argparse.ArgumentParser(prog="helium-cli")
    # parser.add_argument("--silent", action="store_true", help="Run quietly without displaying decorations")
    # subparsers = parser.add_subparsers(title="subcommands")
    #
    # if "--silent" not in argv:
    #     print(utils.get_title())
    #
    # for action in actions:
    #     action.setup(subparsers)
    #
    # if len(argv) == 1:  # pragma: no cover
    #     parser.print_help()
    #
    #     return
    #
    # args = parser.parse_args(argv[1:])
    #
    # if not hasattr(args, "action"):  # pragma: no cover
    #     parser.print_help()
    #
    #     return
    #
    # args.action.run(args)
    #
    # print("")


if __name__ == '__main__':
    cli()
