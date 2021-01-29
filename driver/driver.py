from abc import abstractmethod, ABC


# ToDo: Documentação
class Driver(ABC):
    def __init__(self, apps_path: str, env: dict = None):
        self.netapps = set()
        self.env = env or {} # Definir variáveis de ambiente
        self.apps_path = apps_path

    @abstractmethod
    def download(self, identifier: str, uri: str, strategy: str) -> None: # ToDo: Estratégia para definir forma de obtenção do pacote
        raise NotImplementedError

    @abstractmethod
    def remove(self, identifier: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def run_management_action(self, identifier: str, action: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_execution_data(self) -> dict:
        # Definir dados coletados pelo Driver do ambiente de execução
        raise NotImplementedError
