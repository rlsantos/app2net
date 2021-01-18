import json
import asyncio


async def main():
    try:
        while True:
            print("========== Simple Switch Driver Menu =============")
            message = input(
                "1. Instalar programa\n"
                "2. Desinstalar programa\n"
                "3. Obter informações de execução\n"
                "4. Executar ação de gerenciamento\n"
            )
            
            dict_message = {}

            if message == "1":
                dict_message["action"] = "download"
                uri = "something"
                uris = []
                while uri != "":
                    uri = input("URI (Deixe em branco para prosseguir): ")
                    if uri:
                        uris.append(uri)
                dict_message["uris"] = uris
                dict_message["identifier"] = input("Identificador: ")
            elif message == "2":
                dict_message["action"] = "remove"
                dict_message["identifier"] = input("Identificador: ")
            elif message == "3":
                dict_message["action"] = "data"
            elif message == "4":
                dict_message["action"] = "management"
                dict_message["command"] = input("Comando")

            reader, writer = await asyncio.open_connection("localhost", 5555)
            
            writer.write(json.dumps(dict_message).encode())
            response = await reader.read(1024)

            print(response.decode())
    except KeyboardInterrupt:
        pass

asyncio.run(main())
