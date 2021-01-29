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
                dict_message["identifier"] = input("Identificador: ")
                dict_message["extra"] = {}

                n = input("Do you want to include extra data? (Y/N)").upper() == "Y"
                counter = 1
                while n:
                    key = input(f"Extra data [{counter}] - key: ")
                    value = input(f"Extra data [{counter}] - value: ")
                    dict_message["extra"][key] = value
                    counter += 1
                    n = input("Do you want to include more data? (Y/N)").upper() == "Y"

            elif message == "2":
                dict_message["action"] = "remove"
                dict_message["identifier"] = input("Identifier: ")

            elif message == "3":
                dict_message["action"] = "data"

            elif message == "4":
                dict_message["action"] = "management"
                dict_message["identifier"] = input("NetApp Identifier: ")
                dict_message["command"] = input("Command: ")

            reader, writer = await asyncio.open_connection(host, port)
            
            writer.write(json.dumps(dict_message).encode())
            response = await reader.read(1024)

            print(response.decode())

    except KeyboardInterrupt:
        pass

asyncio.run(main())
