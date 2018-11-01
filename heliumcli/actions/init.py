import os
import shutil
import subprocess
import sys
from distutils.dir_util import copy_tree

import git

from .. import utils

__author__ = 'Alex Laird'
__copyright__ = 'Copyright 2018, Helium Edu'
__version__ = '1.4.0'


class InitAction:
    def __init__(self):
        self.name = "init"
        self.help = "Initialize a new project that is compatible with helium-cli"

    def setup(self, subparsers):
        parser = subparsers.add_parser(self.name, help=self.help)
        parser.add_argument("id", help="The ID (no spaces) to give to the new project")
        parser.add_argument("name", help="The friendly name to give to the new project")
        parser.add_argument("host", help="The hostname to give the project")
        parser.add_argument("github_user", help="The GitHub username or project name")
        parser.set_defaults(action=self)

    def run(self, args):
        config_path = os.path.abspath(os.environ.get("HELIUMCLI_CONFIG_PATH", ".heliumcli.yml"))
        if os.path.exists(config_path):
            print("It looks like a helium-cli project already exists in this directory, not doing anything.")

            sys.exit(1)

        utils.get_config(True)

        self._init_project(args)

        print("A new helium-cli project has been initialized.")

    def _init_project(self, args):
        template_project_name = "template-project"

        print("Cloning the template-project repo into this directory ...")
        git.Repo.clone_from("{}/{}.git".format("https://github.com/HeliumEdu", template_project_name),
                            template_project_name)

        copy_tree(template_project_name, ".")
        shutil.rmtree(template_project_name)
        shutil.rmtree(".git")

        repo = git.Repo.init(".")

        print("Updating template variables ...")

        upper_slug = args.id.replace("-", "_").replace(" ", "_").upper()
        lower_slug = upper_slug.lower()

        for dir_name, dirs, files in os.walk("."):
            for filename in files:
                path = os.path.join(dir_name, filename)
                with open(path, "r") as f:
                    s = f.read()
                s = s.replace("{%PROJECT_ID%}", args.id)
                s = s.replace("{%PROJECT_ID_UPPER%}", upper_slug)
                s = s.replace("{%PROJECT_ID_LOWER%}", lower_slug)
                s = s.replace("{%PROJECT_NAME%}", args.name)
                s = s.replace("{%PROJECT_GITHUB_USER%}", args.github_user)

                with open(path, "w") as f:
                    f.write(s)

        repo.git.add(A=True)

        os.rename("project_id", lower_slug)

        print("Running make ...")

        subprocess.call(["make", "install"])
