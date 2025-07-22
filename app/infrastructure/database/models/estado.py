from sqlalchemy import Column, Integer, String
from app.infrastructure.database.models.base import Base

class Estado(Base):
    __tablename__ = 'estado'

    cod_uf = Column(Integer, primary_key=True)
    uf = Column(String(2))
    cod_fornecedor = Column(Integer)
    nome = Column(String(100))