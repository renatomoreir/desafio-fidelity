from abc import ABC, abstractmethod

class Repository(ABC):

    @abstractmethod
    def salvar_resultado(self, resultado: int, idfiltro: int) -> None:
        pass

    @abstractmethod
    def salvar_processos(self, processo: dict, idfiltro: int, resultado: int) -> None:
        pass