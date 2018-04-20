import datetime
import os
import shutil
import subprocess

import git

from . import utils

__author__ = 'Alex Laird'
__copyright__ = 'Copyright 2018, Helium Edu'
__version__ = '1.1.0'


class PrepCodeAction:
    def __init__(self):
        self.name = "prep-code"
        self.help = "Prepare code for release build, updating version and copyright information in project files"

        self.__project_name = utils.get_project_name()
        self.__current_year = str(datetime.date.today().year)
        self.__current_version = None

    def setup(self, subparsers):
        parser = subparsers.add_parser(self.name, help=self.help)
        parser.set_defaults(action=self)

    def run(self, args):
        config = utils.get_config()
        root_dir = utils.get_deploy_root_dir()
        projects_dir = os.path.join(root_dir, "projects")

        for line in open(os.path.join(projects_dir, config["versionInfo"]["project"], config["versionInfo"]["path"])):
            if config["versionInfo"]["path"].endswith(".py") and line.startswith("__version__ = "):
                self.__current_version = line.strip().split("__version__ = '")[1].rstrip("'")

        if not self.__current_version:
            print("WARN: helium-cli does not know how to process this type of file for version information: {}".format(
                config["versionInfo"]["path"]))

            return

        for project in config["projects"]:
            project_dir = os.path.join(projects_dir, project)

            repo = git.cmd.Git(project_dir)
            repo.fetch(tags=True, prune=True)
            repo = git.Repo(project_dir)

            versions_list = repo.tags
            versions_list.sort(key=lambda v: list(map(int, v.tag.tag.lstrip("v").split("."))))

            if len(versions_list) == 0:
                print("No tags have been created yet.")

                return

            latest_tag = versions_list[-1]
            changes = latest_tag.commit.diff(None)

            print("Checking the " + str(len(changes)) + ' file(s) in "' +
                  project + '" that have been modified since ' + latest_tag.tag.tag + " was tagged ...")
            print("-------------------------------")

            count = 0
            for change in changes:
                file_path = os.path.join(project_dir, change.b_rawpath.decode("utf-8"))

                if os.path.exists(file_path) and not os.path.isdir(file_path) and \
                                os.path.splitext(file_path)[1] in [".py", ".js", ".jsx", ".css", ".scss"]:
                    count = self._process_file(count, file_path)

            print("-------------------------------")
            print("Updated " + str(count) + " version and copyright header(s).")
            print("")

            if os.path.exists(os.path.join(project_dir, "package.json")):
                self._process_file(0, os.path.join(projects_dir, "frontend", "package.json"))

                # This is to ensure the lock file also gets updated
                subprocess.call(['npm', '--prefix', project_dir, 'install'])

    def _process_file(self, count, file_path):
        filename = os.path.basename(file_path)
        initial_file = open(file_path, "r")
        new_file = open(file_path + ".tmp", "w")

        updated = False
        for line in initial_file:
            if file_path.endswith(".py"):
                line, count, updated = self._process_python_line(count, updated, file_path, line)
            elif file_path.endswith(".js") or file_path.endswith(".jsx") or \
                    file_path.endswith(".css") or file_path.endswith(".scss"):
                line, count, updated = self._process_js_or_css_line(count, updated, file_path, line)
            elif filename == "package.json":
                line, count, updated = self._process_package_json(count, updated, file_path, line)

            new_file.write(line)

        initial_file.close()
        new_file.close()

        if updated:
            shutil.copy(file_path + ".tmp", file_path)
        os.remove(file_path + ".tmp")

        return count

    def _process_python_line(self, count, updated, file_path, line):
        if utils.should_updated(line, "__version__ = '{}'".format(self.__current_version), "__version__ ="):
            print("Updating " + file_path)

            line = "__version__ = '{}'\n".format(self.__current_version)
            count += 1
            updated = True
        elif utils.should_updated(line,
                                  "__copyright__ = 'Copyright {}, {}'".format(self.__current_year, self.__project_name),
                                  "__copyright__ = ", "{}'".format(self.__project_name)):
            print("Updating " + file_path)

            line = "__copyright__ = 'Copyright {}, {}'\n".format(self.__current_year, self.__project_name)
            count += 1
            updated = True

        return line, count, updated

    def _process_js_or_css_line(self, count, updated, file_path, line):
        if utils.should_updated(line, "* @version " + self.__current_version, "* @version"):
            print("Updating " + file_path)

            line = " * @version {}\n".format(self.__current_version)
            count += 1
            updated = True
        elif utils.should_updated(line, "* Copyright (c) {} {}.".format(self.__current_year, self.__project_name),
                                  "* Copyright (c)", "{}.".format(self.__project_name)):
            print("Updating " + file_path)

            line = " * Copyright (c) {} {}.\n".format(self.__current_year, self.__project_name)
            count += 1
            updated = True

        return line, count, updated

    def _process_package_json(self, count, updated, file_path, line):
        if utils.should_updated(line, "\"version\": \"{}\",".format(self.__current_version), "\"version\": \""):
            print("Updating version in " + file_path)

            line = "  \"version\": \"{}\",\n".format(self.__current_version)
            count += 1
            updated = True

        return line, count, updated
