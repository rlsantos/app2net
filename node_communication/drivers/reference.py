from abc import abstractmethod, ABC


# ToDo: Documentação
class Driver(ABC):
    """Reference App2net Driver interface

    Attributes:
        netapps (set): Identifiers of NetApps installed on the node
        env (dict): Environment variables

            Default Environment Variables:
                - APPS_PATH: Path to install NetApps
                - LOGS_PATH: Path to create driver logs
    """

    def __init__(self, apps_path: str, env: dict = None):
        self.netapps = set()
        self.env = env or {} # Definir variáveis de ambiente
        self.apps_path = apps_path

    @abstractmethod
    def download(self, identifier: str, uri: str, strategy: str) -> None:
        """Download and unpacks the NetApp file

        Args:
            identifier (str): Identifier of the NetApp
            uri (str): URI location of the file. Must be a `.tar.gz` file
            strategy (str): Strategy used to obtain the file
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
    def run_management_action(self, identifier: str, action: str) -> dict:
        """Run a management command of some NetApp

        The command is run on the NetApp root directory

        Args:
            identifier (str): NetApp identifier
            action (str): Command to execute. Variables to be fullfilled are specified between dollar signs
        
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
