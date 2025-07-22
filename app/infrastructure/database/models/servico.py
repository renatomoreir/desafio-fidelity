from sqlalchemy import Boolean, Column, Integer, String
from app.infrastructure.database.models.base import Base

class Servico(Base):
    __tablename__ = 'servico'

    cod_servico = Column(Integer, primary_key=True)
    civil = Column(Boolean, default=False)
    criminal = Column(Boolean, default=False)