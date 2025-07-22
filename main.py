from app.domain.entities.filtro import Filtro
from app.domain.services.scraping_service import ScrapingService
from app.infrastructure.database.postgresdb_repository import PostgresDBRepository
from app.domain.services.pesquisa_service import PesquisaService
from app.core.logger import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    repo = PostgresDBRepository()
    scraping = ScrapingService()
    service = PesquisaService(repo, scraping)

    try:
        filtros = [
            Filtro(tipo='cpf', id_filtro=1, valor="12345678901"),
            # Filtro(tipo='rg', id_filtro=2, valor="4567890"),
            Filtro(tipo='nome', id_filtro=3, valor="Renato Moreira")
        ]
        logger.info(f"Iniciando processamento com {len(filtros)} filtros.")
        service.executar(filtros)
    except Exception as e:
        logger.error(f"Erro na execução: {e}")