import time

from bs4 import BeautifulSoup as bs

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from app.domain.entities.filtro import Filtro
from app.core.config import URL_BASE, URL_EXTENSION
from app.core.logger import get_logger
from app.utils import formatar_data, formatar_valor, get_driver_path, reiniciar_programa

logger = get_logger(__name__)

DRIVER_PATH = get_driver_path()

class ScrapingService():

    def carregar_site(self, filtro: Filtro, documento = str) -> str:
        if not filtro:
            raise ValueError("Lista de filtros não pode estar vazia.")
        if not documento:
            raise ValueError("Documento não pode ser vazio.")
        
        options = Options()
        # options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        try:
            processos = []
            service = Service(executable_path=DRIVER_PATH)
            browser = webdriver.Edge(service=service, options=options)

            browser.get(URL_BASE + URL_EXTENSION)

            select_el = browser.find_element('xpath', '//*[@id="cbPesquisa"]')
            select_ob = Select(select_el)

            if filtro.tipo in ['cpf', 'rg']:
                select_ob.select_by_value('DOCPARTE')
                browser.find_element('xpath', '//*[@id="campo_DOCPARTE"]').send_keys(documento)
            elif filtro.tipo == 'nome':
                select_ob.select_by_value('NMPARTE')
                browser.find_element('xpath', '//*[@id="pesquisarPorNomeCompleto"]').click()
                browser.find_element('xpath', '//*[@id="campo_NMPARTE"]').send_keys(documento)

            browser.find_element('xpath', '//*[@id="botaoConsultarProcessos"]').click()
            time.sleep(3)

            page_index = 1

            while True:
                dados = self.processo_extracao(browser)
                processos.extend(dados)

                try:
                    next_btn = browser.find_element(By.CSS_SELECTOR, 'a.unj-pagination__next')
                    if "disabled" in next_btn.get_attribute("class"):
                        break
                    next_btn.click()
                    time.sleep(3)
                    page_index += 1
                except NoSuchElementException:
                    logger.info("Sem mais páginas.")
                    break

            browser.quit()
            return processos

        except Exception as e:
            logger.info(f"[ERRO] carregar_site falhou: {e}")
            time.sleep(10)
            reiniciar_programa()


    def processo_extracao(self, driver) -> list[dict]:
        results = []
        soup = bs(driver.page_source, "html.parser")
        items = soup.select("ul.unj-list-row > li")
        if not items:
            items = soup.select(".unj-entity-header")
            if not items:
                logger.info("Nenhum item encontrado na página.")
                return []
            else:
                for item in items:
                    processo = self.processo_detalhe(item)
                    results.append(processo)
                    return results

        for item in items:
            try:
                link_tag = item.select_one(".linkProcesso")
                process_number = link_tag.get_text(strip=True) if link_tag else None
                relative_url = link_tag['href'] if link_tag else None
                full_url = URL_BASE + relative_url if relative_url else None

                name_div = item.select_one(".nomeParte")
                if not name_div:
                    participant_name = (item.select_one(".classeProcesso").get_text(strip=True) + " " + item.select_one(".assuntoPrincipalProcesso").get_text(strip=True))
                else:
                    participant_name = name_div.get_text(strip=True) 

                if process_number and full_url:
                    logger.info(f"Visiting: {full_url}")
                    driver.get(full_url)
                    time.sleep(3)
        
                    parsed = self.processo_detalhe(bs(driver.page_source, "html.parser"))
                    parsed["codigo_processo"] = process_number
                    parsed["nome_completo"] = participant_name or parsed.get("nome_completo")

                    results.append(parsed)

            except Exception as e:
                logger.info(f"[Erro ao processar item]: {e}")
                continue

        return results
    
    def processo_detalhe(self, soup: any) -> dict:
        def get_text(selector):
            el = soup.select_one(selector)
            return el.text.strip() if el else None

        return {
            "classe": get_text('#classeProcesso'),
            "assunto": get_text('#assuntoProcesso'),
            "juiz": get_text('#juizProcesso'),
            "foro": get_text('#foroProcesso'),
            "vara": get_text('#varaProcesso'),
            "data_distribuicao": formatar_data(get_text('#dataHoraDistribuicaoProcesso')),
            "controle": get_text('#numeroControleProcesso'),
            "area": get_text('#areaProcesso'),
            "valor": formatar_valor(get_text('#valorAcaoProcesso')),
            "nome_completo": get_text('#nomeParteEAdvogado'),
            "codigo_processo": get_text('#numeroProcesso'), 
        }