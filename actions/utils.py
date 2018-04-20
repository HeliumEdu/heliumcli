import json
import os
from configparser import ConfigParser

import yaml
from dotenv import load_dotenv

__author__ = 'Alex Laird'
__copyright__ = 'Copyright 2018, Helium Edu'
__version__ = '1.1.0'

VERSION = __version__

_config_cache = None

load_dotenv()


def get_title():
    return """\
    __         ___                            ___
   / /_  ___  / (_)_  ______ ___        _____/ (_)
  / __ \/ _ \/ / / / / / __ `__ \______/ ___/ / /
 / / / /  __/ / / /_/ / / / / / /_____/ /__/ / /
/_/ /_/\___/_/_/\__,_/_/ /_/ /_/      \___/_/_/
                                              v{}
""".format(VERSION)


def _create_default_config(config_path):
    data = {
        "gitProject": os.environ.get("HELIUMCLI_GIT_PROJECT", "git@github.com:HeliumEdu"),
        "projects": json.loads(os.environ.get("HELIUMCLI_PROJECTS", '["platform", "frontend"]')),
        "deployRootRelative": "../../..",
        "versionInfo": {
            "project": os.environ.get("HELIUMCLI_VERSION_INFO_PROJECT", "platform"),
            "path": os.environ.get("HELIUMCLI_VERSION_INFO_PATH", "conf/configs/common.py"),
        },
    }

    with open(config_path, "w") as config_file:
        yaml.dump(data, config_file)


def get_config():
    global _config_cache

    config_path = os.path.join(get_heliumcli_dir(), "config.yml")

    if not _config_cache:
        if not os.path.exists(config_path):
            _create_default_config(config_path)

        with open(config_path, "r") as lines:
            _config_cache = yaml.load(lines)

    return _config_cache


def get_heliumcli_dir():
    return os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))


def get_deploy_root_dir():
    return os.path.abspath(os.path.join(get_heliumcli_dir(), get_config()["deployRootRelative"]))


def parse_hosts_file(env):
    config = ConfigParser()
    config.read(os.path.join(get_deploy_root_dir(), 'ansible/hosts'))

    hosts = []
    for section in config.sections():
        if section.startswith(env):
            for item, section_vars in config.items(section):
                host = item.split(' ')[0]
                section_vars = '{}={}'.format(item.split(' ')[1], section_vars)

                user = 'ubuntu'
                for var in section_vars.split(' '):
                    split = var.split('=')
                    if split[0] == 'ansible_user':
                        user = split[1]
                hosts.append([user, host])

    return hosts


def should_updated(line, verification, start_needle, end_needle=""):
    needs_update = False

    if line.strip().startswith(start_needle) and line.strip().endswith(end_needle):
        if line.strip() != verification:
            needs_update = True

    return needs_update


def get_project_name():
    with open(os.path.join(get_deploy_root_dir(), "ansible", "group_vars", "all.yml"), 'r') as lines:
        data = yaml.load(lines)
        return data["project_developer"]
