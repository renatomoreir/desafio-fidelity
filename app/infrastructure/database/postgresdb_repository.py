from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.logger import get_logger
from app.core.config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
from app.domain.interface.repository import Repository
from app.infrastructure.database.models.base import Base
from app.infrastructure.database.models.estado import Estado
from app.infrastructure.database.models.lote import Lote
from app.infrastructure.database.models.lote_pesquisa import LotePesquisa
from app.infrastructure.database.models.pesquisa import Pesquisa as PesquisaModel
from app.infrastructure.database.models.servico import Servico
from app.infrastructure.database.models.pesquisa_spv import PesquisaSPV


class PostgresDBRepository(Repository):
    def __init__(self):
        connection_string = (
            f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )

        self.engine = create_engine(
            connection_string,
            echo=False,
            future=True
        )

        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            future=True
        )

        Base.metadata.create_all(bind=self.engine)
        self.connection = self.engine.connect()
        self.session = self.SessionLocal()
        self.session.expire_on_commit = False
        logger = get_logger(__name__)
        logger.info("Conexão com o banco de dados estabelecida com sucesso.")
        logger.info("Tabelas criadas com sucesso.")
      

    def salvar_resultado(self, resultado: int, idfiltro: int) -> None:
        sql = text("""
            INSERT INTO pesquisa_spv (
            cod_spv, cod_spv_computador, cod_spv_tipo, resultado, cod_funcionario, filtro, website_id
            ) 
            VALUES (NULL, NULL, NULL, :resultado, NULL, :filtro, NULL)
        """)
        self.connection.execute(sql, {
            "resultado": resultado,
            "filtro": idfiltro
        })
        self.connection.commit()


    def salvar_processos(self, processo: dict, filtro_id: int, resultado: int) -> None:
        try:
            with self.engine.connect() as conn:
                trans = conn.begin()
                try:
                    cod_uf = self.obter_estado(conn, "SP")

                    hoje = datetime.now().date()

                    pesquisa_sql = text("""
                        SELECT cod_pesquisa FROM pesquisa
                        WHERE nome = :nome AND data_entrada = :data_entrada
                    """)
                    pesquisa_params = {
                        "nome": processo.get("nome_completo"),
                        "data_entrada": processo.get("data_distribuicao")
                    }
                    existing = conn.execute(pesquisa_sql, pesquisa_params).fetchone()

                    if existing:
                        if not getattr(self, "UPDATE_EXISTING", False):
                            print(f"Pulando processo já existente: {processo.get('codigo_processo')}")
                            trans.commit()
                            return
                        else:
                            print(f"Atualizando processo existente: {processo.get('codigo_processo')}")
                            cod_pesquisa = existing[0]
                    else:
                        sql_pesquisa = text("""
                            INSERT INTO pesquisa (
                                cod_cliente, cod_uf, cod_servico, tipo,
                                cpf, cod_uf_nascimento, cod_uf_rg,
                                data_entrada, data_conclusao,
                                nome, nome_corrigido,
                                rg, rg_corrigido, nascimento,
                                mae, mae_corrigido, anexo
                            ) VALUES (
                                :cod_cliente, :cod_uf, :cod_servico, :tipo,
                                :cpf, :cod_uf_nascimento, :cod_uf_rg,
                                :data_entrada, :data_conclusao,
                                :nome, :nome_corrigido,
                                :rg, :rg_corrigido, :nascimento,
                                :mae, :mae_corrigido, :anexo
                            ) RETURNING cod_pesquisa
                        """)
                        pesquisa_values = {
                            "cod_cliente": getattr(self, "pesquisa", None) and self.pesquisa.cod_cliente,
                            "cod_uf": cod_uf,
                            "cod_servico": getattr(self, "pesquisa", None) and self.pesquisa.cod_servico,
                            "tipo": filtro_id,
                            "cpf": getattr(self, "pesquisa", None) and self.pesquisa.cpf,
                            "cod_uf_nascimento": None,
                            "cod_uf_rg": None,
                            "data_entrada": processo.get("data_distribuicao"),
                            "data_conclusao": processo.get("data_distribuicao"),
                            "nome": processo.get("nome_completo"),
                            "nome_corrigido": processo.get("nome_completo"),
                            "rg": getattr(self, "pesquisa", None) and self.pesquisa.rg,
                            "rg_corrigido": getattr(self, "pesquisa", None) and self.pesquisa.rg,
                            "nascimento": None,
                            "mae": None,
                            "mae_corrigido": None,
                            "anexo": None
                        }
                        result = conn.execute(sql_pesquisa, pesquisa_values)
                        cod_pesquisa = result.fetchone()[0]

                    cod_lote = self.obter_lote(conn)

                    lote_pesquisa_sql = text("""
                        SELECT 1 FROM lote_pesquisa WHERE cod_pesquisa = :cod_pesquisa AND cod_lote = :cod_lote
                    """)
                    exists_lote = conn.execute(lote_pesquisa_sql, {
                        "cod_pesquisa": cod_pesquisa,
                        "cod_lote": cod_lote
                    }).fetchone()

                    if not exists_lote:
                        sql_lote_pesquisa = text("""
                            INSERT INTO lote_pesquisa (
                                cod_lote, cod_pesquisa, cod_funcionario, cod_funcionario_conclusao,
                                cod_fornecedor, data_entrada, data_conclusao, cod_uf, obs
                            ) VALUES (:cod_lote, :cod_pesquisa, -1, -1, -1, :data_entrada, :data_conclusao, :cod_uf, NULL)
                        """)
                        conn.execute(sql_lote_pesquisa, {
                            "cod_lote": cod_lote,
                            "cod_pesquisa": cod_pesquisa,
                            "data_entrada": hoje,
                            "data_conclusao": hoje,
                            "cod_uf": cod_uf
                        })

                    pesquisa_spv_sql = text("""
                        INSERT INTO pesquisa_spv (
                            cod_pesquisa, cod_spv, cod_spv_computador, cod_spv_tipo,
                            resultado, cod_funcionario, filtro, website_id
                        ) VALUES (:cod_pesquisa, 1, 36, NULL, :resultado, -1, :filtro, 1)
                        ON CONFLICT (cod_pesquisa, cod_spv, filtro)
                        DO UPDATE SET resultado = EXCLUDED.resultado
                    """)

                    conn.execute(pesquisa_spv_sql, {
                        "cod_pesquisa": cod_pesquisa,
                        "resultado": resultado,
                        "filtro": filtro_id
                    })

                    trans.commit()
                except Exception as e:
                    trans.rollback()
                    print(f"[ERRO SALVAR DB]: {e}")
        except Exception as e:
            print(f"[ERRO CONEXÃO DB]: {e}")
        

    def obter_estado(self, conn, uf: str) -> int:
        sql_select = text("SELECT cod_uf FROM estado WHERE uf = :uf")
        result = conn.execute(sql_select, {"uf": uf}).fetchone()
        if result:
            return result[0]
        sql_insert = text("INSERT INTO estado (uf) VALUES (:uf) RETURNING cod_uf")
        return conn.execute(sql_insert, {"uf": uf}).fetchone()[0]


    def obter_lote(self, conn) -> int:
        sql_select = text("SELECT cod_lote FROM lote ORDER BY cod_lote DESC LIMIT 1")
        result = conn.execute(sql_select).fetchone()
        if result:
            return result[0]
        sql_insert = text("""
            INSERT INTO lote (descricao, cod_funcionario, tipo, prioridade)
            VALUES (:descricao, NULL, 'automatica', 'normal') RETURNING cod_lote
        """)
        return conn.execute(sql_insert, {"descricao": "Lote Automático"}).fetchone()[0]
