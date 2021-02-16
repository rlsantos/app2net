from abc import abstractmethod, ABC
import os

from ..env_storage import EnvStorage


class Driver(ABC):
    """Reference App2net Driver interface

    Attributes:
        netapps (set): Identifiers of NetApps installed on the node
        env (EnvStorage): Environment variables

            Default Environment Variables:
                - APPS_PATH: Path to install NetApps
                - LOGS_PATH: Path to create driver logs

    Todos:
        - Specify default environment variables
    """

    def __init__(self, env_file: str = 'env.sqlite3', env: dict = None):
        self.netapps = set()
        self.env = EnvStorage(env_file)

        default_env = {
            "APPS_PATH": os.path.join(os.getcwd(), 'netapps'),
            "LOGS_PATH": os.path.join(os.getcwd(), 'logs'),
        }
        default_env.update(env or {})
        for key, value in default_env.items():
            self.env[key] = value

    @abstractmethod
    def download(self, identifier: str, uri: str, strategy: str, hash: str) -> None:
        """Download and unpack the NetApp file

        Args:
            identifier (str): Identifier of the NetApp
            uri (str): URI location of the file. Must be a `.tar.gz` file
            strategy (str): Strategy used to obtain the file
            hash (str): Hash used to validate the package integrity
        """
        raise NotImplementedError

    @abstractmethod
    def remove(self, identifier: str) -> None:
        """Uninstall and delete all files of a NetApp

        Args:
            identifier (str): Identifier of NetApp to be removed
        """
        raise NotImplementedError

    @abstractmethod
    def run_management_action(self, identifier: str, action: str,
                              native_procedure: bool = False) -> dict:
        """Run a management command of some NetApp

        The command is run on the NetApp root directory

        Args:
            identifier (str): NetApp identifier
            action (str): Command to execute. 
                Commands can use variables by specifying them between dollar signs
            native_procedure (bool): Mark that some platform-specific action need to
                be included before the netapp action.
                Examples:
                    Openflow: Stop and restart the controller
                    P4: Stop switch, compile program and restart switch


        Returns:
            dict: Dictionary with the commands output
        """
        raise NotImplementedError

    @abstractmethod
    def get_execution_data(self) -> dict:
        """Provides data about the execution environment

        Returns:
            dict: Dictionary containing relevant information

        Todos:
            - Specify default data
        """

        # Definir dados coletados pelo Driver do ambiente de execução
        raise NotImplementedError
