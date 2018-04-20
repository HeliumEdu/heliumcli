import os
import subprocess

from . import utils

__author__ = 'Alex Laird'
__copyright__ = 'Copyright 2018, Helium Edu'
__version__ = '1.1.0'

child_processes = []


class StartServersAction:
    def __init__(self):
        self.name = "start-servers"
        self.help = "Launch servers to run locally"

    def setup(self, subparsers):
        parser = subparsers.add_parser(self.name, help=self.help)
        parser.set_defaults(action=self)

    def run(self, args):
        config = utils.get_config()
        root_dir = utils.get_deploy_root_dir()

        # Ensure prerequisites installed
        for project in config["projects"]:
            subprocess.call(["make", "install", "-C", os.path.join(root_dir, "projects", project)])

        # Identify dev servers (if present) and launch them
        for project in config["projects"]:
            # Check if Django project
            if os.path.exists(os.path.join(root_dir, "projects", project, "manage.py")):
                subprocess.Popen(os.path.join(root_dir, "projects", project, ".venv", "bin", "python") + " " +
                                 os.path.join(root_dir, "projects", project, "manage.py") + " runserver",
                                 shell=True)
            # Check if NPM project
            elif os.path.exists(os.path.join(root_dir, "projects", project, "package.json")):
                subprocess.Popen("npm run start --prefix " + os.path.join(root_dir, "projects", project),
                                 shell=True).wait()
