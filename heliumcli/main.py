#!/usr/bin/env python

import argparse
import sys

from heliumcli.actions.listbuilds import ListBuildsAction
from . import utils
from .actions.buildrelease import BuildReleaseAction
from .actions.deploybuild import DeployBuildAction
from .actions.init import InitAction
from .actions.prepcode import PrepCodeAction
from .actions.setbuild import SetBuildAction
from .actions.startservers import StartServersAction
from .actions.update import UpdateAction
from .actions.updateprojects import UpdateProjectsAction

__author__ = "Alex Laird"
__copyright__ = "Copyright 2018, Helium Edu"
__version__ = "1.6.0"


def main(argv):
    actions = {
        InitAction(),
        UpdateAction(),
        UpdateProjectsAction(),
        SetBuildAction(),
        StartServersAction(),
        PrepCodeAction(),
        BuildReleaseAction(),
        DeployBuildAction(),
        ListBuildsAction(),
    }

    parser = argparse.ArgumentParser(prog="helium-cli")
    parser.add_argument("--silent", action="store_true", help="Run quietly without displaying decorations")
    subparsers = parser.add_subparsers(title="subcommands")

    if "--silent" not in argv:
        print(utils.get_title())

    for action in actions:
        action.setup(subparsers)

    if len(argv) == 1:  # pragma: no cover
        parser.print_help()

        return

    args = parser.parse_args(argv[1:])

    if not hasattr(args, "action"):  # pragma: no cover
        parser.print_help()

        return

    args.action.run(args)

    print("")


if __name__ == "__main__":
    main(sys.argv)
