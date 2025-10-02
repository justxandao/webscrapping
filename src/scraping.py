import time
import re
import logging
import random
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# configuração do logging para detalhar erros
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extrair_detalhes_anuncio(html_conteudo: str) -> dict:
    soup = BeautifulSoup(html_conteudo, 'html.parser')
    #construtor
    detalhes = {
        'nome_anuncio': None,
        'nota_media': None,
        'total_avaliacoes': None,
        'localizacao': None,
        'valor_noite': None,
        'datas_disponiveis': []
    }

    try:
        # nome do anuncio
        nome_elemento = soup.find('h1')
        if nome_elemento:
            detalhes['nome_anuncio'] = nome_elemento.text.strip()
            
        # avaliações
        secao_avaliacoes = soup.find('div', {'data-section-id': 'REVIEWS_DEFAULT'})
        if secao_avaliacoes:
            # caso esteja dentro de um header
            header_avaliacoes = secao_avaliacoes.find('h2')
            if header_avaliacoes and '·' in header_avaliacoes.text:
                partes = header_avaliacoes.text.split('·')
                nota_match = re.search(r'(\d[,.]\d+)', partes[0])
                if nota_match:
                    detalhes['nota_media'] = float(nota_match.group(1).replace(',', '.'))
                total_match = re.search(r'(\d+)', partes[1])
                if total_match:
                    detalhes['total_avaliacoes'] = int(total_match.group(1))
            # caso esteja em outro formato
            else:
                nota_el = soup.select_one('div[data-testid="pdp-reviews-highlight-banner-host-rating"] div[aria-hidden="true"]')
                total_el = soup.select_one('div[data-testid="pdp-reviews-highlight-banner-host-review"] span')
                if nota_el and total_el:
                    nota_match = re.search(r'(\d[,.]\d+)', nota_el.text)
                    if nota_match:
                        detalhes['nota_media'] = float(nota_match.group(1).replace(',', '.'))
                    total_match = re.search(r'(\d+)', total_el.text)
                    if total_match:
                        detalhes['total_avaliacoes'] = int(total_match.group(1))

        # localização
        secao_localizacao = soup.find('div', {'data-section-id': 'LOCATION_DEFAULT'})
        if secao_localizacao:
            botao_mapa = secao_localizacao.find('button', {'data-testid': 'listing-map-button'})
            div_local = secao_localizacao.find('div', class_='s1qk96pm')
            h3_local = secao_localizacao.find('h3')
            
            if botao_mapa:
                detalhes['localizacao'] = botao_mapa.text.strip()
            elif div_local:
                detalhes['localizacao'] = div_local.text.strip()
            elif h3_local:
                detalhes['localizacao'] = h3_local.text.strip()

        # dias disponiveis
        secao_calendario = soup.find('div', {'data-testid': 'inline-availability-calendar'})
        if secao_calendario:
            dias_disponiveis = secao_calendario.select('div[data-is-day-blocked="false"]')
            lista_datas = [dia.get('data-testid').replace('calendar-day-', '') for dia in dias_disponiveis if dia.get('data-testid')]
            detalhes['datas_disponiveis'] = lista_datas

        # preços
        secao_reserva = soup.find('div', {'data-plugin-in-point-id': 'BOOK_IT_SIDEBAR'})
        if secao_reserva:
            valor_total_para_calculo = None
            preco_promocao = secao_reserva.find('span', class_=re.compile(r'umuerxh'))
            # caso o valor esteja em promoção
            if preco_promocao:
                preco_texto = preco_promocao.text.strip()
                match = re.search(r'(\d[\d.]*)', preco_texto.replace(',', '.'))
                if match:
                    valor_total_para_calculo = float(match.group(1).replace('.', ''))
            else:
                preco_normal_el = secao_reserva.select_one('div._w3xh25 span, span._10d7v0r span')
                if preco_normal_el:
                    preco_texto = preco_normal_el.text.strip().split(" ")[0]
                    match = re.search(r'(\d[\d.]*)', preco_texto.replace(',', '.'))
                    if match:
                        valor_total_para_calculo = float(match.group(1).replace('.', ''))
            
            if valor_total_para_calculo is not None:
                valor_por_noite = valor_total_para_calculo / 2
                detalhes['valor_noite'] = valor_por_noite

    except Exception as e:
        logging.error(f"Erro: {e}")

    return detalhes

# codigo principal
servico = Service(ChromeDriverManager().install())
opcoes = webdriver.ChromeOptions()
navegador = webdriver.Chrome(service=servico, options=opcoes)
dados_airbnb = []

try:
    url = 'https://www.airbnb.com.br/'
    navegador.get(url)
    navegador.maximize_window()
    espera = WebDriverWait(navegador, 10)

    try:
        botao_cookie = espera.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Aceitar") or contains(text(), "OK")]')))
        logging.info("Pop-up encontrado. Fechando.")
        botao_cookie.click()
        time.sleep(2)
    except TimeoutException:
        logging.info("Nenhum pop-up encontrado.")

    try:
        logging.info("Aguardando os anúncios carregarem.")
        WebDriverWait(navegador, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='card-container']")))
    except TimeoutException:
        logging.critical("Os cards de anúncio não carregaram a tempo.")
        raise

    elementos = navegador.find_elements(By.CSS_SELECTOR, "[data-testid='card-container']")
    links = [el.find_element(By.TAG_NAME, "a").get_attribute('href') for el in elementos if el.find_elements(By.TAG_NAME, "a")]

    if not links:
        logging.warning("Nenhum link de anúncio foi encontrado.")
    else:
        numero_anuncios = 10
        logging.info(f"\nEncontrados {len(links)} links. Processando os {numero_anuncios} primeiros...")
        
        for i, link in enumerate(links[:numero_anuncios]):
            logging.info(f"\n--- Processando Anúncio {i+1}/{numero_anuncios} ---")
            
            try:
                navegador.execute_script("window.open(arguments[0], '_blank');", link)
                navegador.switch_to.window(navegador.window_handles[1])
                
                WebDriverWait(navegador, 25).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-section-id="REVIEWS_DEFAULT"]')))
                logging.info("Página do anúncio carregada.")
                time.sleep(random.uniform(2, 4))

                html_anuncio = navegador.page_source
                detalhes_anuncio = extrair_detalhes_anuncio(html_anuncio)
                detalhes_anuncio['link'] = link
                
                dados_airbnb.append(detalhes_anuncio)
                logging.info(f"Coletando os dados de: {detalhes_anuncio.get('nome_anuncio', 'N/A')}")

            except TimeoutException:
                logging.error(f"Página do anúncio não carregou a tempo: {link}")
            except Exception as e:
                logging.error(f"Erro inesperado ao processar o link {link}: {e}")
            finally:
                if len(navegador.window_handles) > 1:
                    navegador.close()
                    navegador.switch_to.window(navegador.window_handles[0])
                time.sleep(random.uniform(1.5, 3.5))

    logging.info("\nSalvando dados no arquivo.")
    try:
        with open('hospedagens.json', 'w', encoding='utf-8') as f:
            if dados_airbnb:
                json.dump(dados_airbnb, f, ensure_ascii=False, indent=4)
                logging.info("Arquivo salvado.")
            else:
                logging.warning("Nenhum dado foi coletado para salvar.")
    except Exception as e:
        logging.error(f"Erro ao salvar: {e}")

finally:
    if navegador:
        navegador.quit()
    logging.info("Navegador encerrado.")