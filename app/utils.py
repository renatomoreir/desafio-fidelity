import os
import re
import sys
import platform
import unicodedata
from datetime import datetime
from app.core.logger import get_logger
from app.core.config import CONSTA01, CONSTA02, DRIVER_LINUX, DRIVER_WIN, NADA_CONSTA

logger = get_logger(__name__)


def remover_acentuacao(texto: str) -> str:
    if not isinstance(texto, str):
        return str(texto)

    nfkd_form = unicodedata.normalize('NFKD', texto)
    only_ascii = nfkd_form.encode('ascii', 'ignore')
    return only_ascii.decode('utf-8')


def formatar_data(data_str: str) -> datetime.date:
    if not data_str:
        return None

    dt_obj = None
    
    match = re.match(r'(\d{2}/\d{2}/\d{4} às \d{2}:\d{2})', data_str)

    if match:
        data_hora_limpa_str = match.group(1)
        try:
            dt_obj = datetime.strptime(data_hora_limpa_str, '%d/%m/%Y às %H:%M')
        except ValueError as e:
            logger.info(f"Erro ao formatar data/hora extraída '{data_hora_limpa_str}': {e}")
    else:
        try:
            dt_obj = datetime.strptime(data_str, '%d/%m/%Y')
        except ValueError as e:
            logger.info(f"Data inválida ou em formato desconhecido: '{data_str}' - {e}")

    if dt_obj:
        return dt_obj.strftime("%Y-%m-%d %H:00")
    
    return None


def formatar_valor(valor_str: str) -> str:
    if not valor_str:
        return None
    try:
        return valor_str.replace('R$', '').replace('.', '').replace(',', '.').strip()
    except ValueError:
        logger.info(f"Valor inválido: '{valor_str}'")
        return None


def reiniciar_programa():
    try:
        python = sys.executable
        os.execl(python, python, *sys.argv)
    except Exception:
        logger.info('PROGRAMA ENCERRADO')
        quit()

        
def checar_resultado(processo: any) -> int:
    if NADA_CONSTA in processo:
        return 1
    elif (
        'criminal' in remover_acentuacao(processo.get('area', '').lower()) or
        'civil' in remover_acentuacao(processo.get('area', '').lower()) or
        'civel' in remover_acentuacao(processo.get('area', '').lower())
    ):
        return 2
    elif CONSTA01 in processo or CONSTA02 in processo:
        return 5
    return 7


def get_driver_path() -> str:
    if platform.system() == "Windows":
        return os.path.join(DRIVER_WIN)
    else:
        return os.path.join(DRIVER_LINUX)
