__copyright__ = "Copyright (c) 2018 Helium Edu"
__license__ = "MIT"

import datetime
import os
import shutil
import subprocess

import git

from .. import utils


class PrepCodeAction:
    def __init__(self):
        self.name = "prep-code"
        self.help = ("Prepare code for release build, updating version and copyright information "
                     "in project files")

    def setup(self, subparsers):
        parser = subparsers.add_parser(self.name, help=self.help)
        parser.add_argument("--roles", action="store", type=str, nargs="*",
                            help="Limit the project roles to be prepped")
        parser.set_defaults(action=self)

    def run(self, args):
        self._copyright_name = utils.get_copyright_name()
        self._current_year = str(datetime.date.today().year)
        self._current_version = None

        config = utils.get_config()
        projects_dir = utils.get_projects_dir()

        for line in open(os.path.join(projects_dir, config["versionInfo"]["project"],
                                      config["versionInfo"]["path"]),
                         "r"):
            if config["versionInfo"]["path"].endswith(".py") and line.startswith("__version__ = "):
                self._current_version = line.strip().split("__version__ = \"")[1].rstrip("\"")

        if not self._current_version:
            print("WARN: helium-cli does not know how to process this type of file for "
                  "version information: {path}".format(path=config["versionInfo"]["path"]))

            return

        print(f"Prepping code for release with version {self._current_version} ...\n")

        for project in utils.get_projects(config):
            if args.roles and project not in args.roles:
                continue

            if config["projectsRelativeDir"] != ".":
                project_path = os.path.join(projects_dir, project)
            else:
                project_path = os.path.join(projects_dir)

            repo = git.Repo(project_path)
            repo.git.fetch(tags=True, prune=True)

            version_tags = utils.sort_tags(repo.tags)

            if len(version_tags) == 0:
                print("No version tags have been created yet.")

                return

            latest_tag = version_tags[-1]
            changes = latest_tag.commit.diff(None)

            print(f"Checking the {len(changes)} file(s) in \"{project}\" that have been "
                  f"modified since {latest_tag.name} was tagged ...")
            print("-------------------------------")

            count = 0
            for change in changes:
                file_path = os.path.join(project_path, change.b_rawpath.decode("utf-8"))

                if (os.path.exists(file_path) and not os.path.isdir(file_path) and
                        os.path.splitext(file_path)[1] in [".py", ".js", ".jsx", ".css", ".scss"]):
                    if self._process_file(file_path):
                        count += 1

            print("-------------------------------")
            print(f"Updated {count} file(s).")
            print("")

            if os.path.exists(os.path.join(project_path, "package.json")):
                self._process_file(os.path.join(project_path, "package.json"))

                # This is to ensure the lock file also gets updated
                subprocess.call(["npm", "--prefix", project_path, "install"])

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
            print(f"Updated {file_path}.")

            shutil.copy(file_path + ".tmp", file_path)
        os.remove(file_path + ".tmp")

        return updated

    def _process_python_line(self, line):
        if utils.should_update(line,
                               f"__version__ = \"{self._current_version}\"",
                               "__version__ ="):
            line = f"__version__ = \"{self._current_version}\"\n"
            return line, True
        elif utils.get_config()["updateCopyrightYear"] and \
                utils.should_update(line,
                                    f"__copyright__ = \"Copyright (c) {self._current_year}, "
                                    f"{self._copyright_name}\"",
                                    "__copyright__ = ",
                                    f"{self._copyright_name}\""):

            line = f"__copyright__ = \"Copyright (c) {self._current_year} {self._copyright_name}\"\n"
            return line, True
        return line, False

    def _process_js_or_css_line(self, line):
        if utils.should_update(line, "* @version " + self._current_version, "* @version"):
            line = f" * @version {self._current_version}\n"
            return line, True
        elif utils.should_update(line, f"* Copyright (c) {self._current_year} {self._copyright_name}.",
                                 "* Copyright (c)", f"{self._copyright_name}."):
            line = f" * Copyright (c) {self._current_year} {self._copyright_name}.\n"
            return line, True
        return line, False

    def _process_package_json(self, line):
        if utils.should_update(line, f"\"version\": \"{self._current_version}\",", "\"version\": \""):
            line = f"  \"version\": \"{self._current_version}\",\n"
            return line, True
        return line, False
