import json
import os
import subprocess
import sys
from builtins import input

import yaml

__author__ = "Alex Laird"
__copyright__ = "Copyright 2018, Helium Edu"
__version__ = "2.0.0"


class Config:
    def __init__(self):
        self._config_cache = None

    def get_default_settings(self):
        return {
            "gitProject": os.environ.get("HELIUMCLI_GIT_PROJECT", "https://github.com/HeliumEdu"),
            "projects": json.loads(os.environ.get("HELIUMCLI_PROJECTS", "[\"platform\", \"frontend\"]")),
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

    def _save_config(self, config_path, config):
        with open(config_path, "w") as config_file:
            yaml.safe_dump(config, config_file)

    def get_config(self, init=False):
        config_path = os.path.abspath(os.environ.get("HELIUMCLI_CONFIG_PATH", ".heliumcli.yml"))

        if not self._config_cache:
            if not os.path.exists(config_path):
                if not init:  # pragma: no cover
                    response = input("No config file found; initialize a new project [Y/n]? ")
                    if response.lower() not in ["y", "yes", ""]:
                        print("\nThis tool cannot be used without a config file.\n")

                        sys.exit(1)
                    else:
                        print("")

                self._save_config(config_path, self.get_default_settings())

            with open(config_path, "r") as lines:
                self._config_cache = yaml.safe_load(lines)
        else:
            # Ensure cache is up to date
            updated = False
            for key in self.get_default_settings().keys():
                if key not in self._config_cache:
                    self._config_cache[key] = self.get_default_settings()[key]

                    updated = True

            if updated:
                self._save_config(config_path, self._config_cache)

        return self._config_cache

    def get_ansible_dir(self):
        return os.path.abspath(self.get_config()["ansibleRelativeDir"])

    def get_projects_dir(self):
        return os.path.abspath(self.get_config()["projectsRelativeDir"])

    def parse_hosts_file(self, env):
        hosts_str = subprocess.Popen(["ansible", "all", "-i", os.path.join("hosts", env), "--list-hosts"],
                                     cwd=self.get_ansible_dir(), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     bufsize=1).stdout.read().decode("utf-8")

        hosts = []
        for line in hosts_str.split("\n")[1:]:
            if line.strip() != "":
                hosts.append(["ubuntu" if env != "devbox" else "vagrant", line.strip()])

        return hosts

    def get_copyright_name(self):  # pragma: no cover
        with open(os.path.join(self.get_ansible_dir(), "group_vars", "all.yml"), "r") as lines:
            data = yaml.safe_load(lines)
            return data[self.get_config()["ansibleCopyrightNameVar"]]

    def get_repo_name(self, repo_dir):  # pragma: no cover
        remote_url_str = subprocess.Popen(["git", "config", "--get", "remote.origin.url"], cwd=repo_dir,
                                          stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                          bufsize=1).stdout.read().decode("utf-8")
        return os.path.basename(remote_url_str.strip()).rstrip(".git")

    def get_projects(self, config):
        return config["projects"]
