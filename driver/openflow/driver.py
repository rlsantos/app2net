from server import MessageServer
from db_manager import Base
from utils import popen, listdir, mkdir, cd, download, run_command_w_output
import logging

class OpenflowDriver:
    def __init__(self):
        self.home = run_command_w_output('echo $HOME')[:-1]
        self.db = Base(self.home+'/driver')
        home_files = listdir(self.home)
        if not 'netapps' in home_files:
            cd(self.home)
            mkdir('netapps')
        
    
    def download_files(self, netapp_id:str , uris:dict):
        cd(self.home+'/netapps')
        mkdir(netapp_id)

        for uri in uris:
            cd(self.home+'/netapps/'+netapp_id)
            mkdir(uri)
            cd(uri)
            download(url=uris[uri])        

    def handle_message(self, message: dict) -> None:
        action = message["action"]
        if action == "new_netapp":
            self.new_netapp(message['identifier'], message['name'], message['netapp_actions'], message['initial_action'], message['uris'])

        elif action == "execute":
            netapp_id = message["identifier"]
            action_name = message["action_name"]
            exe = self.run_manage_action(netapp_id, action_name)
            if not exe:
                return exe

        elif action == "get_exe_data":
            pass

        else:
            error = f"Unknow action: {action}"
            #logging.error(error)
            raise ValueError(error)

    def run_manage_action(self, netapp_identifier: str, action_name: str):
        command = self.db.get_netapp_action(netapp_identifier, action_name)
        if command:
            cd(self.home+'/netapps/'+netapp_identifier)
            popen(command)
            return None

        else:
            return "Error: invalid parameters"


    def new_netapp(self, identifier: str, name: str, actions: dict, initial: str, uris:dict):
        self.db.insert_netapp(identifier, name, actions, uris)
        self.download_files(identifier, uris)
        self.run_manage_action(identifier, initial)

    def get_execution_data(self):
        pass

if __name__ == "__main__":
    driver = OpenflowDriver()
    with MessageServer("", 5555, driver.handle_message) as server:
        server.run()
