import os
import subprocess

import git

from .. import utils

__author__ = "Alex Laird"
__copyright__ = "Copyright 2019, Helium Edu"
__version__ = "2.0.0"


class DeployBuildAction:
    def run(self, args):
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
                        print("WARN: if you want to get the latest code updates, verify your network connection.")
                    else:
                        raise ex

                if len(repo.git.diff(args.version, "master")) > 0:
                    repo.git.checkout(args.version)
                else:
                    repo.git.checkout("master")

        version = args.version.lstrip("v")
        hosts = utils.parse_hosts_file(args.env)
        for host in hosts:
            subprocess.call(["ssh", "-t", "{}@{}".format(host[0], host[1]),
                             config["hostProvisionCommand"]])

        playbook_options = ["--inventory-file={}/hosts/{}".format(ansible_dir, args.env), "-v",
                            "--extra-vars", "build_version={}".format(version)]

        if args.migrate or args.code or args.envvars or args.conf or args.ssl:
            tags = []
            if args.code:
                tags.append("code")
            if args.migrate:
                tags.append("migrate")
            if args.envvars:
                tags.append("envvars")
            if args.conf:
                tags.append("conf")
            if args.ssl:
                tags.append("ssl")
            playbook_options.append("--tags")
            playbook_options.append(",".join(tags))

        if args.roles:
            playbook_options.append("--limit")
            playbook_options.append(",".join(args.roles))

        subprocess.call(["ansible-playbook"] + playbook_options + ["{}/{}.yml".format(ansible_dir, args.env)])
