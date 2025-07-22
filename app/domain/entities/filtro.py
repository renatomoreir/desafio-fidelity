from typing import Optional
from dataclasses import dataclass


@dataclass
class Filtro:
    tipo: str = ""  # CPF, RG, Nome
    id_filtro: int = 0
    valor: str = ""
    nome: Optional[str] = None
    rg: Optional[str] = None
    cpf: Optional[str] = None
    cod_cliente: int = None
    cod_servico: int = None

    def get_filtro(self) -> str:
        if self.tipo == 'cpf':
            self.cpf = self.valor
            return self.cpf
        elif self.tipo == 'rg':
            self.rg = self.valor
            return self.rg
        elif self.tipo == 'nome':
            self.nome = self.valor
            return self.nome
        raise ValueError("Filtro inválido! Deve ser com os dados correspondentes preenchidos")
