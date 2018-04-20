#!/usr/bin/env python

import argparse
import sys

from .lib import utils
from .lib.buildrelease import BuildReleaseAction
from .lib.deploybuild import DeployBuildAction
from .lib.pullcode import PullCodeAction
from .lib.startservers import StartServersAction
from .lib.updateheaders import UpdateHeadersAction

__author__ = 'Alex Laird'
__copyright__ = 'Copyright 2018, Helium Edu'
__version__ = utils.VERSION


def main(argv):
    actions = {
        PullCodeAction(),
        StartServersAction(),
        UpdateHeadersAction(),
        BuildReleaseAction(),
        DeployBuildAction(),
    }

    parser = argparse.ArgumentParser(prog="helium-cli")
    parser.add_argument("--silent", action="store_true", help="Run more quietly, not displaying decorations")
    subparsers = parser.add_subparsers(title="subcommands")

    silent = '--silent' in argv
    if not silent:
        print(utils.get_title())

    for action in actions:
        action.setup(subparsers)

    if len(argv) == 1:
        parser.print_help()

        return

    args = parser.parse_args()

    if not hasattr(args, 'action'):
        parser.print_help()

        return

    args.action.run(args)

    print("")


if __name__ == "__main__":
    main(sys.argv)
