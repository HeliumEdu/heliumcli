import os
import subprocess

import click
import git

from .. import utils

__author__ = "Alex Laird"
__copyright__ = "Copyright 2019, Helium Edu"
__version__ = "2.0.0"


class DeployBuildCommand:
    def __init__(self, ctx, version, env, roles, migrate, code, envvars, conf, ssl):
        self.ctx = ctx
        self.version = version
        self.env = env
        self.roles = roles
        self.migrate = migrate
        self.code = code
        self.envvars = envvars
        self.conf = conf
        self.ssl = ssl

    def run(self):
        config = utils.get_config()
        ansible_dir = utils.get_ansible_dir()

        if config["projectsRelativeDir"] != ".":
            root_dir = os.path.abspath(os.path.join(ansible_dir, ".."))
            if os.path.exists(os.path.join(root_dir, ".git")):
                repo = git.Repo(root_dir)
                try:
                    repo.git.fetch(tags=True, prune=True)
                except git.GitCommandError as ex:
                    if ex.status == 128:
                        click.echo("WARN: if you want to get the latest code updates, verify your network connection.")
                    else:
                        raise ex

                if len(repo.git.diff(self.version, "master")) > 0:
                    repo.git.checkout(self.version)
                else:
                    repo.git.checkout("master")

        version = self.version.lstrip("v")
        hosts = utils.parse_hosts_file(self.env)
        for host in hosts:
            subprocess.call(["ssh", "-t", "{}@{}".format(host[0], host[1]),
                             config["hostProvisionCommand"]])

        playbook_options = ["--inventory-file={}/hosts/{}".format(ansible_dir, self.env), "-v",
                            "--extra-vars", "build_version={}".format(version)]

        if self.migrate or self.code or self.envvars or self.conf or self.ssl:
            tags = []
            if self.code:
                tags.append("code")
            if self.migrate:
                tags.append("migrate")
            if self.envvars:
                tags.append("envvars")
            if self.conf:
                tags.append("conf")
            if self.ssl:
                tags.append("ssl")
            playbook_options.append("--tags")
            playbook_options.append(",".join(tags))

        if self.roles:
            playbook_options.append("--limit")
            playbook_options.append(",".join(self.roles))

        subprocess.call(["ansible-playbook"] + playbook_options + ["{}/{}.yml".format(ansible_dir, self.env)])
