import datetime
import os
import shutil
import subprocess

import click
import git

from .. import utils

__author__ = "Alex Laird"
__copyright__ = "Copyright 2019, Helium Edu"
__version__ = "2.0.0"


class PrepCodeCommand:
    def __init__(self, ctx, roles):
        self.ctx = ctx
        self.roles = roles

        self._copyright_name = self.ctx.config.get_copyright_name()
        self._current_year = str(datetime.date.today().year)
        self._current_version = None

    def run(self):
        config = self.ctx.config.get_config()
        projects_dir = self.ctx.config.get_projects_dir()

        for line in open(os.path.join(projects_dir, config["versionInfo"]["project"], config["versionInfo"]["path"]),
                         "r"):
            if config["versionInfo"]["path"].endswith(".py") and line.startswith("__version__ = "):
                self._current_version = line.strip().split("__version__ = \"")[1].rstrip("\"")

        if not self._current_version:
            click.echo(
                "WARN: helium-cli does not know how to process this type of file for version information: {}".format(
                    config["versionInfo"]["path"]))

            return

        for project in self.ctx.config.get_projects(config):
            if self.roles and project not in self.roles:
                continue

            if config["projectsRelativeDir"] != ".":
                project_path = os.path.join(projects_dir, project)
            else:
                project_path = os.path.join(projects_dir)

            repo = git.Repo(project_path)
            repo.git.fetch(tags=True, prune=True)

            version_tags = utils.sort_tags(repo.tags)

            if len(version_tags) == 0:
                click.echo("No version tags have been created yet.")

                return

            latest_tag = version_tags[-1]
            changes = latest_tag.commit.diff(None)

            click.echo(
                "Checking the {} file(s) in \"{}\" that have been modified since {} was tagged ...".format(len(changes),
                                                                                                           project,
                                                                                                           latest_tag.tag.tag))
            click.echo("-------------------------------")

            count = 0
            for change in changes:
                file_path = os.path.join(project_path, change.b_rawpath.decode("utf-8"))

                if os.path.exists(file_path) and not os.path.isdir(file_path) and os.path.splitext(file_path)[1] in \
                        [".py", ".js", ".jsx", ".css", ".scss"]:
                    if self._process_file(file_path):
                        count += 1

            click.echo("-------------------------------")
            click.echo("Updated {} file(s).".format(count))
            click.echo("")

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
            click.echo("Updated {}.".format(file_path))

            shutil.copy(file_path + ".tmp", file_path)
        os.remove(file_path + ".tmp")

        return updated

    def _process_python_line(self, line):
        if utils.should_update(line, "__version__ = \"{}\"".format(self._current_version), "__version__ ="):

            line = "__version__ = \"{}\"\n".format(self._current_version)
            return line, True
        elif utils.should_update(line,
                                 "__copyright__ = \"Copyright {}, {}\"".format(self._current_year,
                                                                               self._copyright_name),
                                 "__copyright__ = ", "{}\"".format(self._copyright_name)):

            line = "__copyright__ = \"Copyright {}, {}\"\n".format(self._current_year, self._copyright_name)
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
