import json
import asyncio


async def main():
    try:
        print("Connection")
        host = input("Host (default: localhost): ") or 'localhost'
        port = int(input("Port (default: 5555): ") or 5555)
        while True:
            print("========== Node Driver Menu =============")
            message = input(
                "1. Install NetApp\n"
                "2. Remove NetApp\n"
                "3. Get execution data\n"
                "4. Run management action\n"
            )
            
            dict_message = {}

            if message == "1":
                dict_message["action"] = "download"
                dict_message["uri"] = input("URI: ")
                dict_message["identifier"] = input("Identifier: ")
                dict_message["hash"] = input("Package hash: ")

            elif message == "2":
                dict_message["action"] = "remove"
                dict_message["identifier"] = input("Identifier: ")

            elif message == "3":
                dict_message["action"] = "data"

            elif message == "4":
                dict_message["action"] = "management"
                dict_message["identifier"] = input("NetApp Identifier: ")
                dict_message["command"] = input("Command: ")
                dict_message["native_procedure"] = input("Native procedure? (Y/N)").upper() == "Y"

            reader, writer = await asyncio.open_connection(host, port)
            
            writer.write(json.dumps(dict_message).encode())
            response = await reader.read(1024)

            print(response.decode())

    except KeyboardInterrupt:
        pass

asyncio.run(main())
