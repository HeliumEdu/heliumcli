import subprocess

__author__ = "Alex Laird"
__copyright__ = "Copyright 2019, Helium Edu"
__version__ = "2.0.0"


class UpdateCommand:
    def run(self):
        subprocess.call(["pip", "install", "--upgrade", "heliumcli"])
