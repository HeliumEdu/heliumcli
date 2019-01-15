import os
import shutil
import subprocess
import sys

import click
import git

__author__ = "Alex Laird"
__copyright__ = "Copyright 2019, Helium Edu"
__version__ = "2.0.0"


class InitCommand:
    def __init__(self, ctx, id, name, host, github_user, config_only):
        self.ctx = ctx
        self.id = id
        self.name = name
        self.host = host
        self.github_user = github_user
        self.config_only = config_only

    def run(self):
        config_path = os.path.abspath(os.environ.get("HELIUMCLI_CONFIG_PATH", ".heliumcli.yml"))
        if os.path.exists(config_path):
            click.echo("It looks like a helium-cli project already exists in this directory, not doing anything.")

            sys.exit(1)

        self.ctx.config.get_config(True)

        self._upper_slug = self.id.replace("-", "_").replace(" ", "_").upper()
        self._lower_slug = self._upper_slug.lower()

        if not self.config_only:
            self._init_project(config_path)
        else:
            self._replace_in_file(os.path.dirname(config_path), os.path.basename(config_path))

        click.echo("A new helium-cli project has been initialized.")

    def _init_project(self, config_path):
        project_dir = os.path.join(os.path.dirname(config_path), self.id)
        template_project_name = "template-project"
        template_version = "1.1.0"

        click.echo("Cloning the template-project v{} repo into this directory ...".format(template_version))
        git.Repo.clone_from("{}/{}.git".format("https://github.com/HeliumEdu", template_project_name),
                            project_dir,
                            branch=template_version)

        shutil.rmtree(os.path.join(project_dir, ".git"))

        if os.path.exists(os.path.join(project_dir, ".travis.yml.template")):
            os.remove(os.path.join(project_dir, ".travis.yml"))
            os.rename(os.path.join(project_dir, ".travis.yml.template"), os.path.join(project_dir, ".travis.yml"))

        if os.path.exists(os.path.join(project_dir, "Makefile.template")):
            os.remove(os.path.join(project_dir, "Makefile"))
            os.rename(os.path.join(project_dir, "Makefile.template"), os.path.join(project_dir, "Makefile"))

        repo = git.Repo.init(project_dir)

        click.echo("Updating template variables ...")

        for dir_name, dirs, files in os.walk(project_dir):
            for filename in files:
                self._replace_in_file(dir_name, filename)

        repo.git.add(A=True)

        os.rename(os.path.join(project_dir, "project_id"), os.path.join(project_dir, self._lower_slug))

        click.echo("Running make ...")

        subprocess.call(["python3", "-m", "pip", "install", "virtualenv"])
        subprocess.call(["python3", "-m", "virtualenv", os.path.join(project_dir, ".venv")])
        subprocess.call(["make", "install", "-C", project_dir])

    def _replace_in_file(self, dir_name, filename):
        path = os.path.join(dir_name, filename)
        with open(path, "r") as f:
            s = f.read()
        s = s.replace("{%PROJECT_ID%}", self.id)
        s = s.replace("{%PROJECT_ID_UPPER%}", self._upper_slug)
        s = s.replace("{%PROJECT_ID_LOWER%}", self._lower_slug)
        s = s.replace("{%PROJECT_NAME%}", self.name)
        s = s.replace("{%PROJECT_GITHUB_USER%}", self.github_user)

        with open(path, "w") as f:
            f.write(s)
