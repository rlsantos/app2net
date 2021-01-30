import subprocess
import re
import os
import shutil
import logging
import tarfile
import hashlib

from ..message_server import MessageServer
from .reference import Driver


var_regex = re.compile(r'\$(?P<var>\w+)\$')


class SimpleSwitchDriver(Driver):
    def __init__(self, interfaces: list = None, env = None) -> None:
        super().__init__(env=env)
        self._interfaces = interfaces or []
        self._process = None
        self._process_output = None

        if "INSTALLED_NETAPP" in self.env:
            self.netapps.add(self.env["INSTALLED_NETAPP"])
        
        self._logger = logging.getLogger(__name__)
        handler = logging.FileHandler(os.path.join(self.env.get('LOGS_PATH'), 'driver.log'))
        handler.setFormatter(logging.Formatter('%(name)s [%(levelname)s - %(asctime)s] %(message)s'))
        handler.setLevel(logging.INFO)
        self._logger.addHandler(handler)
        self._logger.info("Driver initialized")
        self._start()

    def download(self, identifier, uri, strategy, hash):
        self._logger.info(f"Started download of NetApp '{identifier}' files")
        
        if self.netapps:
            self._logger.warning(f"Cannot download netapp '{identifier}' files. "
                    "Switch has already an installed NetApp")
            raise EnvironmentError("There is already a NetApp installed. Please, uninstall it first")
        
        self.netapps.add(identifier)

        apps_path = self.env["APPS_PATH"]
        old_dir = os.getcwd()
        if not os.path.exists(apps_path):
            self._logger.info(f"Creating directory {apps_path}")
            os.makedirs(apps_path)
        os.chdir(apps_path)

        try:
            os.mkdir(identifier)
            self._logger.info(f"Creating directory '{identifier}' on {apps_path}")
        except FileExistsError:
            self._logger.warning(f"Directory '{identifier}' already exists on {apps_path}")

        os.chdir(identifier)

        self._logger.info(f"Downloading NetApp '{identifier}' from {uri}")
        download = subprocess.run(
            ["curl", uri, "--fail", "--silent", "--show-error", "-o", f"{identifier}.tar.gz"], 
            capture_output=True
        )

        if download.stderr:
            message = f"Couldn't complete download from {uri}: {download.stderr.decode()}"
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
        os.chdir(old_dir)
        self._logger.info(f"Completed download of NetApp '{identifier}'")

    def remove(self, identifier):
        if identifier not in self.netapps:
            raise EnvironmentError(f"NetApp '{identifier}' is not installed")

        self._stop()

        os.chdir(self.env["APPS_PATH"])
        shutil.rmtree(identifier)

        self.netapps.remove(identifier)

        if "INSTALLED_NETAPP" in self.env:
            del self.env["INSTALLED_NETAPP"]
        os.chdir("..")
        self._start()

    def run_management_action(self, identifier, action, native_procedure=False):
        self._logger.info(f"Running management action '{action}'")
        old_dir = os.getcwd()
        os.chdir(os.path.join(self.env["APPS_PATH"], identifier))
        
        if native_procedure:
            cmd = [
                "p4c-bm2-ss", 
                "--std", "p4-16", 
                "-o", "build.json", 
                "--p4runtime-files", "netapp.p4runtime.txt"
            ]
        else:
            cmd = []

        for arg in action.split():
            matches = var_regex.findall(arg)
            for match in matches:
                arg = arg.replace(f"${match}$", self.env.get(match))
            cmd.append(arg)

        if native_procedure:
            self._stop()

        p = subprocess.run(cmd, capture_output=True)

        if native_procedure:
            self.env["INSTALLED_NETAPP"] = identifier
            self._start()

        os.chdir(old_dir)

        return {
            "success": not bool(p.stderr),
            "output": p.stdout.decode(),
        }

    def get_execution_data(self):
        return {
            "running": self._process is not None,
            "installed_netapps": list(self.netapps),
        }

    def _start(self):
        if self._process is not None:
            return

        self._logger.info("Starting SimpleSwitch")
        cmd = ["simple_switch_grpc"]

        for interface in self._interfaces:
            cmd.extend(["-i", f"{interface['port']}@{interface['name']}"])

        if self.netapps:
            identifier = list(self.netapps)[0]
            path = os.path.join(self.env["APPS_PATH"], identifier, "build.json")
            cmd.append(path)
        else:
            cmd.append("--no-p4")
        self._process_output = open(os.path.join(self.env['LOGS_PATH'], 'simple_switch.log'), 'a')
        self._process = subprocess.Popen(cmd, stdout=self._process_output, stderr=self._process_output)
        self._logger.info("Started SimpleSwitch")
    
    def _stop(self):
        if self._process is None:
            return

        self._logger.info("Stopping SimpleSwitch")
        self._process.terminate()
        self._process.wait()
        self._process = None

        self._process_output.close()
        self._process_output = None

        self._logger.info("SimpleSwitch stopped")

if __name__ == "__main__":
    driver = SimpleSwitchDriver(
        env={
            "LOGS_PATH": "/home/p4/app2net/driver/simple_switch/logs",
            "APPS_PATH": "/home/p4/app2net/driver/simple_switch/netapps",
        }
    )

    with MessageServer("", 5555, driver) as server:
        server.run()
