import subprocess

__author__ = "Alex Laird"
__copyright__ = "Copyright 2019, Helium Edu"
__version__ = "2.0.0"


class UpdateAction:
    def run(self, args):
        subprocess.call(["pip", "install", "--upgrade", "heliumcli"])
