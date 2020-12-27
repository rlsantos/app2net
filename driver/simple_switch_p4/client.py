import json
import asyncio


async def main():
    while True:
        print("========== Simple Switch Driver Menu =============")
        message = input(
            "1. Instalar programa\n"
            "2. Desinstalar programa\n"
            "3. Obter informações de execução\n"
        )
        
        dict_message = {}

        if message == "1":
            dict_message["action"] = "download"
            dict_message["uri"] = input("URI do programa: ")
            dict_message["identifier"] = input("Identificador: ")
        elif message == "2":
            dict_message["action"] = "remove"
            dict_message["identifier"] = input("Identificador: ")
        elif message == "3":
            dict_message["action"] = "data"

        reader, writer = await asyncio.open_connection("localhost", 5555)
        
        writer.write(json.dumps(dict_message).encode())
        response = await reader.read(1024)

        print(response.decode())

asyncio.run(main())
