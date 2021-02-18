import logging
import re
import os
import subprocess
import shutil
import tarfile
import hashlib
import sys

from .reference import Driver
from ..message_server import MessageServer

var_regex = re.compile(r'\$(?P<var>\w+)\$')

class OpenFlowDriver(Driver):
    def __init__(self, interfaces: list = None, env: dict = None) -> None:
        super().__init__(env=env)
        self.apps_path = env["APPS_PATH"]

        if "INSTALLED_NETAPP" in self.env:
            self.netapps.add(self.env["INSTALLED_NETAPP"])
        
        self._logger = logging.getLogger(__name__)
        handler = logging.FileHandler(os.path.join(self.env.get('LOGS_PATH'), 'driver.log'))
        handler.setFormatter(logging.Formatter('%(name)s [%(levelname)s - %(asctime)s] %(message)s'))
        handler.setLevel(logging.INFO)
        self._logger.addHandler(handler)
        self._logger.info("Driver initialized")

    def download(self, identifier: str, uri: str, strategy: str, hash):
        self._logger.info(f"Started download of netapp {identifier} files")
        if identifier in self.netapps:
            self._logger.warning(f"Cannot download netapp {identifier} files. Already installed.")
            raise EnvironmentError("There is an already installed netapp. Please, uninstall first.")
        self.netapps.add(identifier)
        base_dir = os.getcwd()
        if not os.path.exists(self.apps_path):
            self._logger.info(f"Creating directory {self.apps_path}")
            os.makedirs(self.apps_path)
        os.chdir(self.apps_path)

        try:
            os.mkdir(identifier)
            self._logger.info(f"Creating directory {identifier}")
        except FileExistsError:
            self._logger.warning(f"Directory {identifier} already exists on {self.apps_path}.")

        os.chdir(identifier)

        self._logger.info(f"Downloading netapp files from {uri}")

        download = subprocess.run(
            ["curl", uri, "--fail", "--silent", "--show-error", "-o", f"{identifier}.tar.gz"], 
            capture_output=True
        )

        if download.stderr:
            message = f"Couldn't complete download from {uri}: {download.stderr.decode()}"
            self.remove(identifier)
            self._logger.error(message)
            raise IOError(message)

        tar = f"{identifier}.tar.gz"
        calculated_hash = hashlib.md5()

        with open(tar, "rb") as file:
            calculated_hash.update(file.read())

        if calculated_hash.hexdigest() != hash:
            self.remove(identifier)
            raise ValueError(f"Package hash {calculated_hash.hexdigest()} doesn't match expected value {hash}")

        tarfile.open(tar).extractall(".")
        os.remove(tar)
        os.chdir(base_dir)

        self._logger.info(f"Completed download of NetApp '{identifier}'")
        
    def remove(self, identifier: str):
        if identifier not in self.netapps:
            raise EnvironmentError(f"NetApp '{identifier}' is not installed")
        
        self._logger.info(f"Removing Netapp {identifier}")

        base_dir = os.getcwd()
        os.chdir(self.apps_path)
        shutil.rmtree(identifier)
        self.netapps.remove(identifier)
        os.chdir(base_dir)
        self._logger.info(f"Netapp {identifier} successfully removed")
        
    def run_management_action(self, identifier, action, native_procedure=False):
        self._logger.info(f"Running management action '{action}'")
        os.chdir(self.apps_path)
        os.chdir(identifier)
        command = []

        for arg in action.split():
            matches = var_regex.findall(arg)
            for match in matches:
                arg = arg.replace(f"${match}$", self.env.get(match))
            command.append(arg)

        execution = subprocess.run(
            command,
            capture_output=True,
            )
        
        self._logger.info(f"Management Action -> {action}\nOutput: {execution}")

        os.chdir(self.apps_path)

        return {
            "success": not bool(execution.stderr),
            "output": execution.stdout.decode(),
        }

    def get_execution_data(self):
        return {
            "installed_netapps": list(self.netapps),
        }

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(__file__)
    driver = OpenFlowDriver(
        env={
            "LOGS_PATH": os.path.join(BASE_DIR, "logs"),
            "APPS_PATH": BASE_DIR
        }
    )

    with MessageServer("", 5555, driver) as server:
        server.run()