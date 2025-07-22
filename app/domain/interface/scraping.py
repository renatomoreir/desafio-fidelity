from abc import ABC, abstractmethod

from app.domain.entities.filtro import Filtro

class Scraping(ABC):

    @abstractmethod
    def carregar_site(self, filtro: Filtro, documento: str) -> str:
        pass

    @abstractmethod
    def checar_resultado(self, html: str) -> int:
        pass
