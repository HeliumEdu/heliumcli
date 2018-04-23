import os

from ...actions import utils

__author__ = 'Alex Laird'
__copyright__ = 'Copyright 2018, Helium Edu'
__version__ = '1.1.1'


def given_runserver_exists(project):
    if not os.path.exists(utils.get_projects_dir()):
        os.mkdir(utils.get_projects_dir())

    if not os.path.exists(os.path.join(utils.get_projects_dir(), project)):
        os.mkdir(os.path.join(utils.get_projects_dir(), project))

    os.mkdir(os.path.join(utils.get_projects_dir(), project, os.path.dirname(utils.get_config()["serverBinFilename"])))
    open(os.path.join(utils.get_projects_dir(), project, utils.get_config()["serverBinFilename"]), "wb").close()


def given_hosts_file_exists():
    if not os.path.exists(utils.get_ansible_dir()):
        os.mkdir(utils.get_ansible_dir())

    hosts_file = open(os.path.join(utils.get_ansible_dir(), utils.get_config()["ansibleHostsFilename"]), "w")
    hosts_file.write("[devbox]\nheliumedu.test ansible_user=vagrant ip_address=10.1.0.10")
    hosts_file.close()

