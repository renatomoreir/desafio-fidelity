from sqlalchemy import Column, Integer, Text, UniqueConstraint
from app.infrastructure.database.models.base import Base

class PesquisaSPV(Base):
    __tablename__ = 'pesquisa_spv'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cod_pesquisa = Column(Integer)
    cod_spv = Column(Integer)
    cod_spv_computador = Column(Integer)
    cod_spv_tipo = Column(Integer)
    cod_funcionario = Column(Integer)
    filtro = Column(Integer)
    website_id = Column(Integer)
    resultado = Column(Text)

    __table_args__ = (
        UniqueConstraint('cod_pesquisa', 'cod_spv', 'filtro', name='uq_pesquisa_spv_key'),
    )
