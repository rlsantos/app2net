from abc import abstractmethod, ABC

class Driver(ABC):
    def __init__(self, env: dict = None):
        self.netapps = set()
        self.env = env or {}

    @abstractmethod
    def download(self, uri, identifier) -> None:
        raise NotImplementedError

    @abstractmethod
    def run_management_action(self, **kwargs) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def get_execution_data(self) -> dict:
        raise NotImplementedError
