import os
import subprocess

import git

from . import utils

__author__ = 'Alex Laird'
__copyright__ = 'Copyright 2018, Helium Edu'
__version__ = '1.1.2'


class DeployBuildAction:
    def __init__(self):
        self.name = "deploy-build"
        self.help = "Deploy the specified build, which may be a versioned release or a branch"

    def setup(self, subparsers):
        parser = subparsers.add_parser(self.name, help=self.help)
        parser.add_argument("version", help="The build version to be deployed, which may be a version or a branch")
        parser.add_argument("env", help="The environment to deploy to")
        parser.add_argument('--hosts', action='store', type=str, nargs='*', help="Limit the hosts to be deployed")
        parser.add_argument("--migrate", action="store_true", help="Install code dependencies and run migrations")
        parser.add_argument("--code", action="store_true", help="Only deploy code")
        parser.add_argument("--envvars", action="store_true", help="Only deploy environment variables")
        parser.add_argument("--conf", action="store_true",
                            help="Only deploy configuration files and restart necessary services")
        parser.add_argument("--ssl", action="store_true",
                            help="Only deploy SSL certificates and restart necessary services")
        parser.set_defaults(action=self)

    def run(self, args):
        ansible_dir = utils.get_ansible_dir()

        root_dir = os.path.abspath(os.path.join(ansible_dir, ".."))
        if os.path.exists(os.path.join(root_dir, ".git")):
            repo = git.Repo(root_dir)
            repo.git.fetch(tags=True, prune=True)
            repo.git.checkout(args.version)

        config = utils.get_config()
        version = args.version.lstrip("v")
        hosts = utils.parse_hosts_file(args.env)

        for host in hosts:
            subprocess.call(["ssh", "-t", "{}@{}".format(host[0], host[1]),
                             utils.get_config()["hostProvisionCommand"]])

        playbook_options = ['--inventory-file={}/{}'.format(ansible_dir, config["ansibleHostsFilename"]), '-v',
                            '--extra-vars', '"build_version={}"'.format(version)]

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
            playbook_options.append('--tags')
            playbook_options.append('"{}"'.format(",".join(tags)))

        if args.hosts:
            playbook_options.append('--limit')
            playbook_options.append('"{}"'.format(",".join(args.hosts)))

        subprocess.call(["ansible-playbook"] + playbook_options + ['{}/{}.yml'.format(ansible_dir, args.env)])
