from sqlalchemy import Column, Integer, Date, Text, ForeignKey
from app.infrastructure.database.models.base import Base

class LotePesquisa(Base):
    __tablename__ = 'lote_pesquisa'
    __table_args__ = {'extend_existing': True}

    cod_lote_pesquisa = Column(Integer, primary_key=True)
    cod_lote = Column(Integer, ForeignKey('lote.cod_lote'))
    cod_pesquisa = Column(Integer, ForeignKey('pesquisa.cod_pesquisa'))
    cod_funcionario = Column(Integer)
    cod_funcionario_conclusao = Column(Integer)
    cod_fornecedor = Column(Integer)
    data_entrada = Column(Date)
    data_conclusao = Column(Date)
    cod_uf = Column(Integer, ForeignKey('estado.cod_uf'))
    obs = Column(Text)