import os
import subprocess
import sys

import git

from .. import utils

__author__ = "Alex Laird"
__copyright__ = "Copyright 2018, Helium Edu"
__version__ = "1.5.0"


class DeployBuildAction:
    def __init__(self):
        self.name = "deploy-build"
        self.help = "Deploy the specified build, which may be a versioned release or a branch"

    def setup(self, subparsers):
        parser = subparsers.add_parser(self.name, help=self.help)
        parser.add_argument("version", help="The build version to be deployed, which may be a version or a branch")
        parser.add_argument("env", help="The environment to deploy to")
        parser.add_argument("--roles", action="store", type=str, nargs="*",
                            help="Limit the project roles to be deployed")
        parser.add_argument("--migrate", action="store_true", help="Install code dependencies and run migrations")
        parser.add_argument("--code", action="store_true", help="Only deploy code")
        parser.add_argument("--envvars", action="store_true", help="Only deploy environment variables")
        parser.add_argument("--conf", action="store_true",
                            help="Only deploy configuration files and restart necessary services")
        parser.add_argument("--ssl", action="store_true",
                            help="Only deploy SSL certificates and restart necessary services")
        parser.set_defaults(action=self)

    def run(self, args):
        config = utils.get_config()
        ansible_dir = utils.get_ansible_dir()

        version = args.version.lstrip("v")

        if config["projectsRelativeDir"] != ".":
            root_dir = os.path.abspath(os.path.join(ansible_dir, ".."))
            if os.path.exists(os.path.join(root_dir, ".git")):
                repo = git.Repo(root_dir)
                try:
                    repo.git.fetch(tags=True, prune=True,
                                   force=os.environ.get("HELIUMCLI_FORCE_FETCH", "False") == "True")
                except git.GitCommandError as ex:
                    if ex.status == 128:
                        print("WARN: if you want to get the latest code updates, verify your network connection.")
                    else:
                        raise ex

                repo.git.checkout(version)

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

        cmd = ["ansible-playbook"] + playbook_options + ["{}/{}.yml".format(ansible_dir, args.env)]
        print("Executing Ansible command: {}".format(cmd))
        ret = subprocess.call(cmd)

        if isinstance(ret, int) and ret != 0:
            if ret < 0:
                print("Error: Ansible killed by signal")
            else:
                print("Error: Ansible failed with return value {}".format(ret))
            sys.exit(1)
