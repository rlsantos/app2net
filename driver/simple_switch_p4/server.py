import socket
import json
import threading


class MessageServer(threading.Thread):
    def __init__(self, address, port, handler, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setDaemon(True)
        self.address = address
        self.port = port
        self.handler = handler
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
            try:
                response = self.handler(data) or "Action executed!"
            except Exception as e:
                response = str(e)
            conn.send(response.encode())
