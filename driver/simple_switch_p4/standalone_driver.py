import subprocess
import logging

from server import MessageServer


class SimpleSwitchDriver:
    def __init__(self, switch_name: str, software_path: str = None, interfaces: list = None) -> None:
        self.switch_name = switch_name
        self.software_path = software_path
        self.interfaces = interfaces or []
        self.process = None
        self.logger = logging.getLogger("STANDALONE_DRIVER")
        file_handler = logging.FileHandler("logs/standalone_driver.log", "a")
        file_handler.setFormatter(logging.Formatter("[%(asctime)s] %(name)s: %(message)s"))
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.INFO)
        self.logger.info("Driver initialized")

    def handle_message(self, message: dict) -> None:
        action = message["action"]
        if action == "install":
            self.install(message["path"])
            self.restart()
        elif action == "start":
            self.start()
        elif action == "stop":
            self.stop()
        elif action == "uninstall":
            self.uninstall()
            self.restart()
        elif action == "update":
            self.update(message["path"])
            self.restart()
        elif action == "status":
            return self.status()
        else:
            error = f"Unknow action: {action}"
            logging.error(error)
            raise ValueError(error)

    def start(self) -> None:
        if self.process is not None:
            raise OSError("Switch is already running")
        
        self.logger.info("Starting Switch")
        args = ["simple_switch_grpc"]
        for interface in self.interfaces:
            args.append(f"-i {interface['port']}@{interface['name']}")

        if self.software_path is None:
            args.append("--no-p4")
        else:
            args.append("build/compiled.json")
        log = open("logs/simple_switch.log", "a")
        self.process = subprocess.Popen(
            args, stdout=log, stderr=log
        )
        self.logger.info(f"Switch running with pid: {self.process.pid}")

    def stop(self) -> None:
        if self.process is None:
            raise OSError("Switch is not running")
        self.logger.info("Stopping switch")
        self.process.terminate()
        self.process = None
        self.logger.info("Switch stopped")

    def status(self):
        return (
            f"Simple Switch:\n"
            f"Running: {self.process is not None}\n"
        )

    def install(self, path) -> None:
        cmd = [
            "p4c-bm2-ss",
            path,
            "-o build/compiled.json",
            "--p4runtime-files build/program.p4info.txt",
            "--p4v 16"
        ]
        compiler = subprocess.run(
            " ".join(cmd),
            stderr=subprocess.PIPE, shell=True
        )
        if compiler.stderr:
            raise IOError(f"Could not compile program:\n {compiler.stderr.decode()}")

        self.software_path = "build/compiled.json"

    def update(self, program) -> None:
        self.uninstall()
        self.install(program)

    def uninstall(self) -> None:
        self.logger.info("Software uninstalled")
        self.software_path = None
    
    def restart(self) -> None:
        if self.process is not None:
            self.stop()
            self.start()


if __name__ == "__main__":
    driver = SimpleSwitchDriver("s1")
    with MessageServer("", 5555, driver.handle_message) as server:
        server.run()
