import json
import os

__author__ = "Alex Laird"
__copyright__ = "Copyright 2024, Helium Edu"
__version__ = "1.6.14"

VERSION = __version__


def get_default_settings():
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
        "remoteName": os.environ.get("HELIUMCLI_REMOTE_NAME", "origin"),
        "branchName": os.environ.get("HELIUMCLI_BRANCH_NAME", "main"),
    }
