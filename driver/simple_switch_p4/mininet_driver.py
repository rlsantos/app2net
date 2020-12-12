import logging
import os
import tempfile
from server import MessageServer

from mininet.node import Switch


class SimpleSwitch(Switch):
    def __init__(self, name, software_path=None, **kwargs):
        super().__init__(name, **kwargs)
        self.name = name
        self.software_path = software_path

    def start(self, controllers=None):
        cmd = ["simple_switch_grpc"]
        for port, intf in self.intfs.items():
            if not intf.IP():
                cmd.extend(['-i', str(port) + "@" + intf.name])
        
        if self.software_path is None:
            cmd.append("--no-p4")
        else:
            cmd.append(self.software_path)

        with tempfile.NamedTemporaryFile() as f:
            self.cmd(" ".join(cmd) + " >logs/switch.log" + "2>&1 & echo $! >> " + f.name)
            pid = int(f.read())
        print(f"Running PID: {pid}")

    def stop(self):
        self.cmd("kill %% simple_switch")
        self.cmd("wait")
        self.deleteIntfs()


class SimpleSwitchDriver(Switch):
    def __init__(self, name: str, **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.switch_name = name
        self.switch = None
        self.software_path = None
        self.switch_args = kwargs
        self.server = None
        self.logger = logging.getLogger("MININET_DRIVER")
        self.logger.addHandler(logging.FileHandler("logs/mininet_driver.log"))
        self.logger.setLevel(logging.INFO)
        
        self.logger.info("[DRIVER] Initializing driver... ")
        self.start_daemon()
        self.logger.info("[DRIVER] Done!")

    def start_daemon(self):
        self.server = MessageServer("", 5555, self.handle_message)
        self.server.start()

    def handle_message(self, message: dict) -> None:
        if message["action"] == "install":
            self.install(message["path"])
            self.restart()
        elif message["action"] == "start":
            self.start()
        elif message["action"] == "stop":
            self.stop()
        elif message["action"] == "uninstall":
            self.uninstall()
            self.restart()
        elif message["action"] == "update":
            self.update(message["path"])
            self.restart()
        else:
            raise ValueError("[DRIVER] Unknown action")

    def start(self, controllers=None) -> None:
        if self.switch is not None:
            raise OSError("Switch is already running")

        logging.info("[DRIVER] >> Starting Switch... ")

        self.switch = SimpleSwitch(self.switch_name, self.software_path, **self.switch_args)
        self.switch.start()

        logging.info("[DRIVER] >> Done!")

    def stop(self) -> None:
        if self.switch is None:
            raise OSError(">> Switch is already stopped")
        logging.info(">> Stopping switch... ")
        self.switch.stop()
        self.switch = None
        logging.info(">> Done!")

    def install(self, path_to_program: str) -> None:
        logging.info(f">> Installing {path_to_program} on switch {self.switch}... ")
        os.system(
            f"p4c-bm2-ss {path_to_program} -o build/compiled.json --p4runtime-files build/program.p4info.txt --p4v 16"
        )
        self.software_path = "build/compiled.json"
        logging.info(">> Done!")

    def update(self, path_to_program: str) -> None:
        self.uninstall()
        self.install(path_to_program)

    def uninstall(self) -> None:
        self.software_path = None

    def restart(self) -> None:
        self.stop()
        self.start()


if __name__ == "__main__":
    from mininet.net import Mininet, CLI

    net = Mininet()
    h1 = net.addHost("h1", ip="10.0.1.1/24", mac="08:00:00:00:01:01")
    h2 = net.addHost("h2", ip="10.0.2.2/24", mac="08:00:00:00:02:02")
    h3 = net.addHost("h3", ip="10.0.3.3/24", mac="08:00:00:00:03:03")
    h4 = net.addHost("h4", ip="10.0.4.4/24", mac="08:00:00:00:04:04")
    h5 = net.addHost("h5", ip="10.0.5.5/24", mac="08:00:00:00:05:05")
    s1 = net.addSwitch("s1", cls=SimpleSwitchDriver)
    net.addLink(h1, s1, port2=1)
    net.addLink(h2, s1, port2=2)
    net.addLink(h3, s1, port2=3)
    net.addLink(h4, s1, port2=4)
    net.addLink(h5, s1, port2=5)
    net.start()

    for i in range(1, 6):
        h = net.get(f"h{i}")
        h.cmd(f"route add default gw 10.0.{i}.{i}0 dev h{i}-eth0")
        h.cmd(f"arp -i h{i}-eth0 -s 10.0.{i}.{i}0 08:00:00:00:0{i}:00")

    CLI(net)
