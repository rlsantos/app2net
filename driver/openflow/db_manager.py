import sqlite3
from utils import run_command_w_output, cd

"""
This class manages the sqlite database used by the driver.
"""

class Base:    

    tables = {
        'netapps': ('identifier', 'name'),
        'actions': ('netapp_identifier', 'name', 'command'),
        'uris'   : ('netapp_identifier', 'uri_name', 'uri')
    } #The 'tables' variable is a dictionary that contains the table name, as stringq, as key, and the columns, as value, as a tuple os strings

    def __init__(self, db_path):
        self.db_path = db_path
        print(self.db_path)

        #LOG
        print("*-*-*- Starting Database Instance -*-*-*")
        print("        - Connecting/Creating database")
        # This is happening when the execute method is called in the first time

        #LOG
        print("        - Verifing tables")

        for table in self.tables.keys():
            #LOG
            print("              -", table, end="")

            result = self.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?",(table,))

            if len(result) == 0:
                self.execute(f"CREATE TABLE {table} {str(self.tables[table])}", ())
            
            #LOG
            print(" OK")
              

    
    def execute(self, command: str, parameter:tuple = ()):
        """
        This function executes an command in sqlite by the String command and the list/tuple variables (Useds y sqlite to replace ? element)
        """
        current_path = run_command_w_output('pwd')[:-1]
        cd(self.db_path)
        connection = sqlite3.connect('base.db')
        cursor = connection.cursor()
        cursor.execute(command, parameter)
        fetch = cursor.fetchall()
        connection.commit()
        connection.close()
        cd(current_path)
        return fetch

    def insert_netapp(self, identifier: str, name: str, actions: dict, uris:dict):
        """
        This function inserts a new netapp in DB by the netapp identifier, the netapp path and the netapps actions.
            identifier : String
            name       : String
            actions    : Dict{ action_name:command }
            uris       : Dict{ uri_name:uri }

        """
        #LOG
        print("\n    DB ---> Inserting netapp ", end="")
        self.execute("INSERT INTO netapps VALUES (?, ?)", (identifier, name))
        for action_name in actions:
            self.execute("INSERT INTO actions VALUES (?, ?, ?)", (identifier, action_name, actions[action_name]))
        
        for uri in uris:
            self.execute("INSERT INTO uris VALUES (?, ?, ?)", (identifier, uri, uris[uri]))

        #LOG
        print("OK")

    def get_netapp_action(self, identifier: str, action_name: str):
        """Returns the netapp action by her identifier and the action name"""

        fetch = self.execute("SELECT command FROM actions WHERE netapp_identifier=? AND name=?", (identifier, action_name))
        if fetch:
            return fetch[0][0]
        
        else:
            #LOG
            print("\n        Theres no netapp found with this parameters\n")
            return None
    
    def get_netapp_uri(self, identifier:str, uri_name:str):

        fetch = self.execute("SELECT uri FROM uris WHERE netapp_identifier=? AND uri_name=?", (identifier, uri_name))

        if fetch:
            return fetch[0][0]
        
        else:
            #LOG
            print("\n        Theres no uri found with this parameters\n")
            return None