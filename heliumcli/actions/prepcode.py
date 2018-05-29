import datetime
import os
import shutil
import subprocess

import git

from .. import utils

__author__ = 'Alex Laird'
__copyright__ = 'Copyright 2018, Helium Edu'
__version__ = '1.1.10'


class PrepCodeAction:
    def __init__(self):
        self.name = "prep-code"
        self.help = "Prepare code for release build, updating version and copyright information in project files"

    def init(self):
        self._copyright_name = utils.get_copyright_name()
        self._current_year = str(datetime.date.today().year)
        self._current_version = None

    def setup(self, subparsers):
        self.init()

        parser = subparsers.add_parser(self.name, help=self.help)
        parser.add_argument('--roles', action='store', type=str, nargs='*',
                            help="Limit the project roles to be prepped")
        parser.set_defaults(action=self)

    def run(self, args):
        config = utils.get_config()
        projects_dir = utils.get_projects_dir()

        for line in open(os.path.join(projects_dir, config["versionInfo"]["project"], config["versionInfo"]["path"]),
                         "r"):
            if config["versionInfo"]["path"].endswith(".py") and line.startswith("__version__ = "):
                self._current_version = line.strip().split("__version__ = '")[1].rstrip("'")

        if not self._current_version:
            print("WARN: helium-cli does not know how to process this type of file for version information: {}".format(
                config["versionInfo"]["path"]))

            return

        for project in config["projects"]:
            if args.roles and project not in args.roles:
                continue

            project_dir = os.path.join(projects_dir, project)

            repo = git.Repo(project_dir)
            repo.git.fetch(tags=True, prune=True)

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

                if os.path.exists(file_path) and not os.path.isdir(file_path) and os.path.splitext(file_path)[1] in \
                        [".py", ".js", ".jsx", ".css", ".scss"]:
                    if self._process_file(file_path):
                        count += 1

            print("-------------------------------")
            print("Updated " + str(count) + " file(s).")
            print("")

            if os.path.exists(os.path.join(project_dir, "package.json")):
                self._process_file(os.path.join(project_dir, "package.json"))

                # This is to ensure the lock file also gets updated
                subprocess.call(['npm', '--prefix', project_dir, 'install'])

    def _process_file(self, file_path):
        filename = os.path.basename(file_path)
        initial_file = open(file_path, "r")
        new_file = open(file_path + ".tmp", "w")

        updated = False
        for line in initial_file:
            line_updated = False

            if file_path.endswith(".py"):
                line, line_updated = self._process_python_line(line)
            elif file_path.endswith(".js") or file_path.endswith(".jsx") or \
                    file_path.endswith(".css") or file_path.endswith(".scss"):
                line, line_updated = self._process_js_or_css_line(line)
            elif filename == "package.json":
                line, line_updated = self._process_package_json(line)
            # TODO: implement other known types

            if line_updated:
                updated = True

            new_file.write(line)

        initial_file.close()
        new_file.close()

        if updated:
            print("Updated " + file_path)

            shutil.copy(file_path + ".tmp", file_path)
        os.remove(file_path + ".tmp")

        return updated

    def _process_python_line(self, line):
        if utils.should_update(line, "__version__ = '{}'".format(self._current_version), "__version__ ="):

            line = "__version__ = '{}'\n".format(self._current_version)
            return line, True
        elif utils.should_update(line,
                                 "__copyright__ = 'Copyright {}, {}'".format(self._current_year, self._copyright_name),
                                 "__copyright__ = ", "{}'".format(self._copyright_name)):

            line = "__copyright__ = 'Copyright {}, {}'\n".format(self._current_year, self._copyright_name)
            return line, True
        return line, False

    def _process_js_or_css_line(self, line):
        if utils.should_update(line, "* @version " + self._current_version, "* @version"):
            line = " * @version {}\n".format(self._current_version)
            return line, True
        elif utils.should_update(line, "* Copyright (c) {} {}.".format(self._current_year, self._copyright_name),
                                 "* Copyright (c)", "{}.".format(self._copyright_name)):
            line = " * Copyright (c) {} {}.\n".format(self._current_year, self._copyright_name)
            return line, True
        return line, False

    def _process_package_json(self, line):
        if utils.should_update(line, "\"version\": \"{}\",".format(self._current_version), "\"version\": \""):
            line = "  \"version\": \"{}\",\n".format(self._current_version)
            return line, True
        return line, False
