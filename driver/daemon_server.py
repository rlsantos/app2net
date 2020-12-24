import socket
import json
import threading


class MessageServer(threading.Thread):
    def __init__(self, address, port, driver, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setDaemon(True)
        self.address = address
        self.port = port
        self.driver = driver
        self.sock = None

    def __enter__(self):
        self.prepare()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.stop()
        if exc_type is KeyboardInterrupt:
            return True
        return False

    def prepare(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.address, self.port))
        self.sock.listen()

    def stop(self):
        self.sock.close()

    def run(self):
        if self.sock is None:
            self.prepare()

        while True:
            conn, _ = self.sock.accept()
            data = json.loads(conn.recv(1024).decode())
            response = {}
            try:
                if data["action"] == "download":
                    self.driver.download(data["uri"], data["identifier"])
                elif data["action"] == "remove":
                    self.driver.remove(data["identifier"])
                elif data["action"] == "management":
                    self.driver.run_management_action(data["command"])
                elif data["action"] == "data":
                    response["data"] = self.driver.get_execution_data()
                response["success"] = True
            except Exception as e:
                response["error"] = str(e)
                response["success"] = False
            conn.send(json.dumps(response).encode())
