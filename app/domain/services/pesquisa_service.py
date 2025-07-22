from app.domain.entities.filtro import Filtro
from app.domain.interface.repository import Repository
from app.core.logger import get_logger
from app.domain.interface.scraping import Scraping
from app.utils import checar_resultado


logger = get_logger(__name__)


class PesquisaService():
    resultado: int = 0

    def __init__(self, repo: Repository, scrap: Scraping):
        self.repo = repo
        self.scraping = scrap

    def executar(self, filtros: list[Filtro]):
        tentativas = 0
        while tentativas < 3:
            if not filtros:
                logger.info("Nenhum filtro disponível para pesquisa.")
                break
            for filtro in filtros:
                documento  = filtro.get_filtro()
                if not documento:
                    logger.warning(f"Documento ausente para pesquisa {filtro.id_filtro}")
                    continue
                try:
                    processos = self.scraping.carregar_site(filtro, documento)
                    if not processos:
                        logger.error(f"HTML vazio para pesquisa {filtro.id_filtro}")
                        continue
                    else:
                        filtros.remove(filtro)
                   
                except Exception as e:
                    logger.error(f"Erro ao processar pesquisa {filtro.id_filtro}: {e}")

        if processos:
            for processo in processos:
                resultado = checar_resultado(processo)
                self.repo.salvar_resultado(resultado, filtro.id_filtro)
                logger.info(f"Pesquisa {filtro.id_filtro} concluída com resultado {resultado}")
                self.repo.salvar_processos(processo, filtro.id_filtro, resultado)
                logger.info(f"Pesquisa {filtro.id_filtro} concluída com resultado {resultado}")