import subprocess
import re
import os
import shutil
import logging

from .daemon_server import MessageServer
from .driver import Driver

# Variáveis:
#   - salvar valores no ambiente de execução? (sqlite?)
#   - modificar valores de variáveis de ambiente é outra ação de gerenciamento?
#       - Se não, isso se converte em um novo método na interface?
# 
# Compilação/Instalação:
#   - No Simple Switch, primeiro compila e depois sobe o switch com o programa compilado.
#   - O desenvolvedor precisa informar o comando de compilação como uma management action de instalação? 
#       - Se sim:
#           - como ele indica que o app2net deve disparar essa ação específica para de fato instalar o programa?
#           - como pode adicionar ao seu comando definido as flags padrão do switch (e.g. caminho de saída dos arquivos compilados, flags de compilação)?
#           - modificar a lista de netapps é outra ação independente da de download/instalação que também é disparada pelo app2net?
#       - Se não, quando a compilação ocorre? Logo após o download do pacote?
#

var_regex = re.compile(r'\$(?P<var>\w+)\$')

class SimpleSwitchDriver(Driver):
    def __init__(self, interfaces: list = None, env: dict = None) -> None:
        default_env = {
            "compiler": "p4c",
            "device_args": "--target bmv2 --arch v1model",
        }
        default_env.update(env)
        super().__init__(default_env)
        self._interfaces = interfaces or []
        self._process = None
        self._start()

    def download(self, uri, identifier):
        if self.netapps:
            raise EnvironmentError("There is already a NetApp installed. Please uninstall it first")

        self._stop()
        self.netapps.clear()

        apps_path = self.env.get("apps_path")

        old_dir = os.getcwd()
        if not os.path.exists(apps_path):
            os.makedirs(apps_path)
        os.chdir(apps_path)

        try:
            os.mkdir(identifier)
        except FileExistsError:
            pass

        os.chdir(identifier)

        download = subprocess.run(
            ["curl", uri,  "-o", "netapp.p4"], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        download.check_returncode()

        compilation = subprocess.run([
            self.env.get("compiler"),
            *self.env.get("device_args").split(), 
            "--std", "p4-16", 
            "-o", "build/",
            "--p4runtime-files", "build/netapp.p4runtime.txt",
            "netapp.p4"
        ])
        compilation.check_returncode()

        self.netapps.add(identifier)
        os.chdir(old_dir)
        self._start()

    def remove(self, identifier):
        if identifier not in self.netapps:
            raise EnvironmentError(f"NetApp '{identifier}' is not installed")
        self._stop()
        old_dir = os.getcwd()
        os.chdir(self.env.get("apps_path"))
        shutil.rmtree(identifier)
        self.netapps.remove(identifier)
        os.chdir(old_dir)
        self._start()

    def run_management_action(self, commmand) -> None:
        command = []

        for arg in command.split():
            matches = var_regex.findall(arg)
            if matches:
                for match in matches:
                    arg = arg.replace(f"${match}$", self.env.get(match))
            command.append(arg)

        p = subprocess.run(command)
        p.check_returncode()

    def get_execution_data(self) -> dict:
        return {
            "running": self._process is not None,
            "installed_netapps": list(self.netapps),
        }

    def _start(self):
        if self._process is not None:
            return

        cmd = ["simple_switch_grpc"]

        for interface in self._interfaces:
            args.append(f"-i {interface['port']}@{interface['name']}")

        if self.netapps:
            identifier = list(self.netapps)[0]
            path = os.path.join(self.env.get("apps_path"), identifier, "build/netapp.json")
            cmd.append(path)
        else:
            cmd.append("--no-p4")
        self._process = subprocess.Popen(cmd)
    
    def _stop(self):
        if self._process is None:
            return
        
        self._process.terminate()
        self._process.wait()
        self._process = None


if __name__ == "__main__":
    driver = SimpleSwitchDriver(
        env={
            "apps_path": "/home/p4/app2net/driver/simple_switch/netapps",
            "logs_path": "/home/p4/app2net/driver/simple_switch/logs",
        }
    )

    with MessageServer("", 5555, driver) as server:
        server.run()
