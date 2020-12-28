import json
import asyncio


async def main():
    while True:
        print("========== Openflow Driver Menu =============")
        message = input(
            "1. New Netapp\n"
            "2. Execute action\n"
        )
        
        dict_message = {}

        if message == "1":
            dict_message['action'] = 'new_netapp'

            print('Insert the netapp identifier:\n-> ', end='')
            dict_message['identifier'] = input()

            print('Insert the netapp name:\n-> ', end='')
            dict_message['name'] = input()

            dict_message['uris'] = {}

            print('\n\nHow many uris do you want to add? ', end="")
            qtd_uris = int(input())

            for new in range(qtd_uris):
                print(f'\n{new + 1}° netapp uri')

                print('    Name: ', end="")
                name = input()

                print('    uri: ', end="")
                uri = input()
                dict_message['uris'][name] = uri

            dict_message['netapp_actions'] = {}

            print('\n\nHow many actions do you want to add? ', end="")
            qtd_actions = int(input())

            for new in range(qtd_actions):
                print(f'\n{new + 1}° netapp action')

                print('    Name: ', end="")
                name = input()

                print('    Command: ', end="")
                command = input()
                dict_message['netapp_actions'][name] = command
            
            print('\nWhat is the initial action?:\n-> ', end='')
            dict_message['initial_action'] = input()

        elif message == "2":        
            dict_message["action"] = 'execute'

            print('What is the netapp identifier?\n -> ', end="")
            dict_message["identifier"] = input()

            print('What is the action name?\n -> ', end="")
            dict_message["action_name"] = input()
            

        reader, writer = await asyncio.open_connection("localhost", 5555)
        
        writer.write(json.dumps(dict_message).encode())
        response = await reader.read(1024)

        print(response.decode())

asyncio.run(main())
