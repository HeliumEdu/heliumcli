import datetime
import os

from heliumcli import utils

__author__ = 'Alex Laird'
__copyright__ = 'Copyright 2018, Helium Edu'
__version__ = '1.1.7'


def given_runserver_exists(project):
    config = utils.get_config(True)

    if not os.path.exists(os.path.join(utils.get_projects_dir(), project)):
        os.makedirs(os.path.join(utils.get_projects_dir(), project))

    os.mkdir(
        os.path.join(utils.get_projects_dir(), project, os.path.dirname(config["serverBinFilename"])))
    open(os.path.join(utils.get_projects_dir(), project, config["serverBinFilename"]), "wb").close()


def given_hosts_file_exists():
    utils.get_config(True)

    if not os.path.exists(os.path.join(utils.get_ansible_dir(), 'hosts')):
        os.makedirs(os.path.join(utils.get_ansible_dir(), 'hosts'))

    hosts_file = open(os.path.join(utils.get_ansible_dir(), 'hosts', 'devbox'), "w")
    hosts_file.write("[devbox]\nheliumedu.test ansible_user=vagrant ip_address=10.1.0.10")
    hosts_file.close()


def given_python_version_file_exists(version='1.2.2'):
    config = utils.get_config(True)

    version_file_path = os.path.join(utils.get_projects_dir(), config["versionInfo"]["project"],
                                     config["versionInfo"]["path"])
    if not os.path.exists(os.path.dirname(version_file_path)):
        os.makedirs(os.path.dirname(version_file_path))

    version_file = open(version_file_path, "w")
    version_file.write("""\"\"\"
Header comments and such.
\"\"\"

import os

__author__ = 'Alex Laird'
__copyright__ = 'Copyright 2017, Helium Edu'
__version__ = '{}'

# ############################
# Project configuration
# ############################
    
# Project information

PROJECT_NAME = os.environ.get('PROJECT_NAME')
MORE_SETTINGS = 'more_settings_after_this'
""".format(version))
    version_file.close()

    return version_file_path


def given_project_package_json_exists(project, version='1.2.2'):
    utils.get_config(True)

    versioned_file_path = os.path.join(utils.get_projects_dir(), project, 'package.json')
    if not os.path.exists(os.path.dirname(versioned_file_path)):
        os.makedirs(os.path.dirname(versioned_file_path))

    versioned_file = open(versioned_file_path, "w")
    versioned_file.write("""{
  "name": "my-project",
  "version": \"""" + version + """\",
  "author": "Alex Laird",
  "dependencies": {
    "npm": "^1.2.3",
    "some-dep": "^4.5.6"
  }
}
""")
    versioned_file.close()

    return versioned_file_path


def given_project_python_versioned_file_exists(project, filename='maths.py'):
    utils.get_config(True)

    versioned_file_path = os.path.join(utils.get_projects_dir(), project, filename)
    if not os.path.exists(os.path.dirname(versioned_file_path)):
        os.makedirs(os.path.dirname(versioned_file_path))

    versioned_file = open(versioned_file_path, "w")
    versioned_file.write("""\"\"\"
Other header comments and such.
\"\"\"
    
__author__ = 'Alex Laird'
__copyright__ = 'Copyright 2017, Helium Edu'
__version__ = '1.2.2'
    
def sum(a, b):
    return a + b
""")
    versioned_file.close()

    return versioned_file_path


def given_project_js_versioned_file_exists(project, filename="maths.js"):
    utils.get_config(True)

    versioned_file_path = os.path.join(utils.get_projects_dir(), project, filename)
    if not os.path.exists(os.path.dirname(versioned_file_path)):
        os.makedirs(os.path.dirname(versioned_file_path))

    versioned_file = open(versioned_file_path, "w")
    versioned_file.write("""/**
 * Copyright (c) 2017 Helium Edu.
 *
 * Some functions and stuff.
 *
 * @author Alex Laird
 * @version 1.2.2
 */
    
function sum(a, b) {
    return a + b
}
""")
    versioned_file.close()

    return versioned_file_path


def verify_versioned_file_updated(test_case, versioned_file_path, version):
    current_version_found = False
    current_year_found = False
    for line in open(versioned_file_path, 'r'):
        if versioned_file_path.endswith('.py'):
            if "__version__ = '{}'".format(version) in line:
                current_version_found = True
            elif "__copyright__ = 'Copyright {}'".format(str(datetime.date.today().year)):
                current_year_found = True
        elif versioned_file_path.endswith('.js'):
            if "* @version {}".format(version) in line:
                current_version_found = True
            elif "* Copyright (c) {}".format(str(datetime.date.today().year)):
                current_year_found = True
        elif os.path.basename(versioned_file_path) == 'package.json':
            current_year_found = True
            if "version\": \"{}\",".format(version) in line:
                current_version_found = True

        if current_version_found and current_year_found:
            break

    test_case.assertTrue(current_version_found)
    test_case.assertTrue(current_year_found)
