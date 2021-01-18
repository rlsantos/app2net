import subprocess
import re
import os
import shutil
import logging
import sqlite3
import pickle

from daemon_server import MessageServer
from driver import Driver


var_regex = re.compile(r'\$(?P<var>\w+)\$')


class SimpleSwitchDriver(Driver):
    def __init__(self, apps_path, interfaces: list = None, env: dict = None) -> None:
        default_env = {
            "compiler": "p4c",
            "device_args": "--target bmv2",
            "logs_path": os.path.join(os.path.dirname(__file__), 'logs'),
        }
        default_env.update(env)
        super().__init__(apps_path, default_env)
        self._interfaces = interfaces or []
        self._process = None
        self._process_output = None
        self._logger = logging.getLogger(__name__)

        handler = logging.FileHandler(os.path.join(self.env.get('logs_path'), 'driver.log'))
        handler.setFormatter(logging.Formatter('%(name)s [%(levelname)s - %(asctime)s] %(message)s'))
        handler.setLevel(logging.INFO)
        self._logger.addHandler(handler)
        self._logger.info("Driver initialized")
        self._start()

    def download(self, identifier, uris):
        self._logger.info(f"Started download of NetApp '{identifier}' files")
        if self.netapps:
            self._logger.warning(f"Cannot download netapp '{identifier}' files. Switch has already an installed NetApp")
            raise EnvironmentError("There is already a NetApp installed. Please, uninstall it first")

        self._stop()

        old_dir = os.getcwd()
        if not os.path.exists(self.apps_path):
            self._logger.info(f"Creating directory {self.apps_path}")
            os.makedirs(self.apps_path)
        os.chdir(self.apps_path)

        try:
            os.mkdir(identifier)
            self._logger.info(f"Creating directory '{identifier}' on {self.apps_path}")
        except FileExistsError:
            self._logger.warning(f"Directory '{identifier}' already exists on {self.apps_path}")

        os.chdir(identifier)

        for uri in uris:
            self._logger.info(f"Downloading NetApp '{identifier}' from {uri}")
            download = subprocess.run(
                ["curl", uri, "--fail", "--silent", "--show-error", "-o", "netapp.p4"], 
                capture_output=True
            )

            if download.stderr:
                message = f"Couldn't complete download from {uri}: {download.stderr.decode()}"
                self._logger.error(message)
                raise IOError(message)

        self._logger.info(f"Compiling NetApp '{identifier}'")
        compilation = subprocess.run([
            self.env.get("compiler"),
            *self.env.get("device_args").split(),
            "--arch", "v1model",
            "--std", "p4-16", 
            "-o", "build/",
            "--p4runtime-files", "build/netapp.p4runtime.txt",
            "netapp.p4"
        ], capture_output=True)

        if compilation.stderr:
            self._logger.error(f"Couldn't compile NetApp '{identifier}': {compilation.stderr}")
        compilation.check_returncode()

        self.netapps.add(identifier)
        os.chdir(old_dir)
        self._start()
        self._logger.info(f"Completed download of NetApp '{identifier}'")


    def remove(self, identifier):
        if identifier not in self.netapps:
            raise EnvironmentError(f"NetApp '{identifier}' is not installed")
        self._stop()
        old_dir = os.getcwd()
        os.chdir(self.apps_path)
        shutil.rmtree(identifier)
        self.netapps.remove(identifier)
        os.chdir(old_dir)
        self._start()

    def run_management_action(self, identifier, action):
        self._logger.info(f"Running management action '{action}'")
        os.chdir(
            os.path.join()
        )
        cmd = []

        for arg in action.split():
            matches = var_regex.findall(arg)
            for match in matches:
                arg = arg.replace(f"${match}$", self.env.get(match))
            cmd.append(arg)

        p = subprocess.run(cmd)
        p.check_returncode()

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
            path = os.path.join(self.apps_path, identifier, "build/netapp.json")
            cmd.append(path)
        else:
            cmd.append("--no-p4")
        self._process_output = open(os.path.join(self.env.get('logs_path'), 'simple_switch.log'), 'a')
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

class EnvStorage:
    def __init__(self, db):
        self.db = sqlite3.connect(db)
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS env ("
                "key TEXT PRIMARY KEY,"
                "value TEXT"
            ")"
        )

    def __getitem__(self, key):
        return self.get(key)

    def get(self, key):
        cursor = self.db.execute("SELECT value FROM env WHERE key=?", [key])
        data = list(cursor)
        if data:
            return self._deserialize(data[0][0])
        else:
            raise Exception("Env has no specified key")

    def __setitem__(self, key, value):
        self.set(key, value)
    
    def set(self, key, value):
        try: 
            self.get(key)
            self.db.execute("UPDATE env SET value=? WHERE key=?;", [self._serialize(value), key])
        except sqlite3.OperationalError:
            self.db.execute("INSERT INTO env VALUES (?, ?);", [key, self._serialize(value)])
        self.db.commit()

    @staticmethod
    def _serialize(value):
        return pickle.dumps(value)

    @staticmethod
    def _deserialize(value):
        return pickle.loads(value)

    def __delitem__(self, key):
        self.delete(key)

    def delete(self, key):
        self.db.execute("DELETE FROM env WHERE key=?", [key])
        self.db.commit()

if __name__ == "__main__":
    driver = SimpleSwitchDriver(
        apps_path="/home/p4/app2net/driver/simple_switch/netapps",
        env={
            "logs_path": "/home/p4/app2net/driver/simple_switch/logs",
        }
    )

    with MessageServer("", 5555, driver) as server:
        server.run()
