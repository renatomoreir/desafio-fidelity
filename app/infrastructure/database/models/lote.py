from sqlalchemy import Column, Integer, String, Date
from app.infrastructure.database.models.base import Base

class Lote(Base):
    __tablename__ = 'lote'

    cod_lote = Column(Integer, primary_key=True)
    cod_lote_prazo = Column(Integer)
    data_criacao = Column(Date)
    cod_funcionario = Column(Integer)
    tipo = Column(String(50))
    prioridade = Column(String(50))
    descricao = Column(String(255))