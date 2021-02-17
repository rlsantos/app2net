import asyncio
import json


class NodeNotifier:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    async def send_message(self, message: dict):
        reader, writer = await asyncio.open_connection(self.host, self.port)

        writer.write(json.dumps(message).encode())
        await writer.drain()

        response = await reader.read(1024)

        writer.close()
        await writer.wait_closed()

        return response.decode()

    async def download(self, uri: str, netapp_identifier: str, hash: str, strategy: str):
        message = {}
        message["action"] = "download"
        message["uri"] = uri
        message["identifier"] = netapp_identifier
        message["hash"] = hash
        message["strategy"] = strategy
        return await self.send_message(message)

    async def remove(self, netapp_identifier: str):
        message = {}
        message["action"] = "remove"
        message["identifier"] = netapp_identifier
        return await self.send_message(message)

    async def get_execution_data(self):
        message = {}
        message["action"] = "data"
        return await self.send_message(message)

    async def run_management_action(self, netapp_identifier: str, command: str, 
                                    native_procedure: bool = False):
        message = {}
        message["action"] = "management"
        message["identifier"] = netapp_identifier
        message["command"] = command
        message["native_procedure"] = native_procedure
        return await self.send_message(message)


if __name__ == "__main__":
    async def main():
        host = input("Host (default: localhost): ") or 'localhost'
        port = int(input("Port (default: 5555): ") or 5555)

        notifier = NodeNotifier(host, port)

        try:
            while True:
                message = input(
                    "1. Install NetApp\n"
                    "2. Remove NetApp\n"
                    "3. Get execution data\n"
                    "4. Run management action\n"
                )

                if message == "1":
                    uri = input("URI: ")
                    identifier = input("Identifier: ")
                    hash = input("Package hash: ")
                    strategy = input("Strategy: ")
                    print(await notifier.download(uri, identifier, hash, strategy))

                elif message == "2":
                    identifier = input("Identifier: ")
                    print(await notifier.remove(identifier))

                elif message == "3":
                    print(await notifier.get_execution_data())

                elif message == "4":
                    identifier = input("NetApp Identifier: ")
                    command  = input("Command: ")
                    native_procedure = input("Native procedure? (Y/N)").upper() == "Y"
                    print(await notifier.run_management_action(identifier, command, native_procedure))

        except KeyboardInterrupt:
            pass
    
    asyncio.run(main())