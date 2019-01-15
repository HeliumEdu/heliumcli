import os
import subprocess

__author__ = "Alex Laird"
__copyright__ = "Copyright 2019, Helium Edu"
__version__ = "2.0.0"

child_processes = []


class StartServersCommand:
    def __init__(self, ctx):
        self.ctx = ctx

    def run(self):
        config = self.ctx.config.get_config()
        projects_dir = self.ctx.config.get_projects_dir()

        # Identify dev servers (if present) and launch them
        processes = []
        for project in self.ctx.config.get_projects(config):
            if config["projectsRelativeDir"] != ".":
                project_path = os.path.join(projects_dir, project)
            else:
                project_path = os.path.join(projects_dir)

            runserver_bin = os.path.join(project_path, config["serverBinFilename"])

            if os.path.exists(runserver_bin):
                processes.append(subprocess.Popen(runserver_bin))

        if len(processes) > 0:
            processes[-1].wait()
