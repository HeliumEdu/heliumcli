import json
import os
import subprocess
import sys
from builtins import input

import yaml

from .version import VERSION

__author__ = 'Alex Laird'
__copyright__ = 'Copyright 2018, Helium Edu'
__version__ = '1.1.10'

_config_cache = None


def get_title():
    return """\
    __         ___                            ___
   / /_  ___  / (_)_  ______ ___        _____/ (_)
  / __ \/ _ \/ / / / / / __ `__ \______/ ___/ / /
 / / / /  __/ / / /_/ / / / / / /_____/ /__/ / /
/_/ /_/\___/_/_/\__,_/_/ /_/ /_/      \___/_/_/
                                              v{}
""".format(VERSION)


def _save_config(config_path, config):
    with open(config_path, "w") as config_file:
        yaml.safe_dump(config, config_file)


def _get_config_defaults():
    return {
        "gitProject": os.environ.get("HELIUMCLI_GIT_PROJECT", "git@github.com:HeliumEdu"),
        "projects": json.loads(os.environ.get("HELIUMCLI_PROJECTS", '["platform", "frontend"]')),
        "projectsRelativeDir": os.environ.get("HELIUMCLI_PROJECTS_RELATIVE_DIR", "projects"),
        "serverBinFilename": os.environ.get("HELIUMCLI_SERVER_BIN_FILENAME", "bin/runserver"),
        "ansibleRelativeDir": os.environ.get("HELIUMCLI_ANSIBLE_RELATIVE_DIR", "ansible"),
        "ansibleCopyrightNameVar": os.environ.get("HELIUMCLI_ANSIBLE_COPYRIGHT_NAME_VAR", "project_developer"),
        "hostProvisionCommand": os.environ.get("HELIUMCLI_HOST_PROVISION_COMMAND",
                                               "sudo apt-get update && sudo apt-get install -y python && sudo apt-get -y autoremove"),
        "versionInfo": {
            "project": os.environ.get("HELIUMCLI_VERSION_INFO_PROJECT", "platform"),
            "path": os.environ.get("HELIUMCLI_VERSION_INFO_PATH", "conf/configs/common.py"),
        },
    }


def get_config(init=False):
    global _config_cache

    config_path = os.path.abspath(os.environ.get("HELIUMCLI_CONFIG_PATH", ".heliumcli.yml"))

    if not _config_cache:
        if not os.path.exists(config_path):
            if not init:
                response = input('No config file found; initialize a new project [Y/n]? ')
                if response.lower() not in ['y', 'yes', '']:
                    print('\nThis tool cannot be used without a config file.\n')

                    sys.exit(1)
                else:
                    print("")

            _save_config(config_path, _get_config_defaults())

        with open(config_path, "r") as lines:
            _config_cache = yaml.safe_load(lines)
    else:
        # Ensure cache is up to date
        updated = False
        for key in _get_config_defaults().keys():
            if key not in _config_cache:
                _config_cache[key] = _get_config_defaults()[key]

                updated = True

        if updated:
            _save_config(config_path, _config_cache)

    return _config_cache


def get_ansible_dir():
    return os.path.abspath(get_config()["ansibleRelativeDir"])


def get_projects_dir():
    return os.path.abspath(get_config()["projectsRelativeDir"])


def parse_hosts_file(env):
    hosts_str = subprocess.Popen(['ansible', 'all', '-i', os.path.join('hosts', env), '--list-hosts'],
                                 cwd=get_ansible_dir(), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 bufsize=1).stdout.read().decode('utf-8')

    hosts = []
    for line in hosts_str.split('\n')[1:]:
        if line.strip() != '':
            hosts.append(['ubuntu' if env != 'devbox' else 'vagrant', line.strip()])

    return hosts


def should_update(line, verification, start_needle, end_needle=""):
    needs_update = False

    if line.strip().startswith(start_needle) and line.strip().endswith(end_needle):
        if line.strip() != verification:
            needs_update = True

    return needs_update


def get_copyright_name():  # pragma: no cover
    with open(os.path.join(get_ansible_dir(), "group_vars", "all.yml"), 'r') as lines:
        data = yaml.safe_load(lines)
        return data[get_config()["ansibleCopyrightNameVar"]]


def get_repo_name(repo_dir):  # pragma: no cover
    remote_url_str = subprocess.Popen(["git", "config", "--get", "remote.origin.url"], cwd=repo_dir,
                                      stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                      bufsize=1).stdout.read().decode('utf-8')
    return os.path.basename(remote_url_str.strip()).rstrip(".git")
