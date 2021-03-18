import socket
import json
import threading

from .drivers.reference import Driver


class MessageServer(threading.Thread):
    """Handle message exchanges with nodes through network

    Receive JSON messages and dispatch them to the node driver
    Each message must have an "action" key and other parameters according it

    Examples:
        - As Context Manager (recommended)::

            with MessageServer("", 5555, Driver()) as server:
                server.run()

        - Simple Usage::

            server = MessageServer("", 5555, Driver())
            server.run()
            # Keep the server thread running while needed. 
            # Call 'stop' when you are done
            server.stop()

    Attributes:
        address (str): Address of the server. Leave blank to use `localhost`
        port (int): Port used by the server
        driver (Driver): Driver that will receive the dispatched messages
    """

    def __init__(self, address: str, port: int, driver: Driver):
        super().__init__()
        self.setDaemon(True)
        self.address = address
        self.port = port
        self.driver = driver
        self.sock = None

    def __enter__(self):
        self._prepare()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.stop()
        if exc_type is KeyboardInterrupt:
            return True
        return False

    def _prepare(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.address, self.port))
        self.sock.listen()

    def stop(self):
        """Close all connections and shuts down the server"""
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        self.sock = None

    def run(self):
        """Start the server"""

        if self.sock is None:
            self._prepare()

        while True:
            conn, _ = self.sock.accept()
            data = json.loads(conn.recv(1024).decode())
            response = {
                "success": True
            }
            try:
                if data["action"] == "download":
                    self.driver.download(data["identifier"],
                                         data["uri"], data["strategy"], data["hash"])
                elif data["action"] == "remove":
                    self.driver.remove(data["identifier"])
                elif data["action"] == "management":
                    output = self.driver.run_management_action(
                        data["identifier"], data["command"], data["native_procedure"])
                    if output is not None:
                        response = output
                elif data["action"] == "data":
                    response["data"] = self.driver.get_execution_data()
            except Exception as e:
                response["error"] = {"type": type(e).__name__, "message": str(e)}
                response["success"] = False
            conn.send(json.dumps(response).encode())
