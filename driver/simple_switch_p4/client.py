import json
import asyncio


async def main():
    while True:
        print("========== Simple Switch Driver Menu =============")
        message = input(
            "1. Instalar programa\n"
            "2. Iniciar switch\n"
            "3. Parar switch\n"
            "4. Desinstalar programa\n"
            "5. Atualizar programa\n"
            "6. Verificar status\n"
        )
        
        dict_message = {}

        if message == "1":
            path = input("Path to program: ")
            dict_message["action"] = "install"
            dict_message["path"] = path
        elif message == "2":
            dict_message["action"] = "start"
        elif message == "3":
            dict_message["action"] = "stop"
        elif message == "4":
            dict_message["action"] = "uninstall"
        elif message == "5":
            dict_message["action"] = "update"
            dict_message["path"] = input("Path to program: ")
        elif message == "6":
            dict_message["action"] = "status"

        reader, writer = await asyncio.open_connection("localhost", 5555)
        
        writer.write(json.dumps(dict_message).encode())
        response = await reader.read(1024)

        print(response.decode())

asyncio.run(main())
