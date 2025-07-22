from sqlalchemy import Column, Integer, String, Date, ForeignKey
from app.infrastructure.database.models.base import Base

class Pesquisa(Base):
    __tablename__ = 'pesquisa'

    cod_pesquisa = Column(Integer, primary_key=True)
    cod_cliente = Column(Integer)
    cod_uf = Column(Integer, ForeignKey('estado.cod_uf'))
    cod_servico = Column(Integer, ForeignKey('servico.cod_servico'))
    tipo = Column(String(50))
    cpf = Column(String(14))
    cod_uf_nascimento = Column(Integer)
    cod_uf_rg = Column(Integer)
    data_entrada = Column(Date)
    data_conclusao = Column(Date)
    nome = Column(String(100))
    nome_corrigido = Column(String(100))
    rg = Column(String(20))
    rg_corrigido = Column(String(20))
    nascimento = Column(Date)
    mae = Column(String(100))
    mae_corrigido = Column(String(100))
    anexo = Column(String(255))