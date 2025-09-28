import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

# Configuração Inicial
service = Service()
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)
url = 'https://www.airbnb.com.br/'
driver.get(url)
driver.maximize_window()

# Lógica para fechar pop-ups na página inicial ---
wait_popup = WebDriverWait(driver, 10)

# Bloco para o pop-up de Cookies
try:
    cookie_button = wait_popup.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Aceitar") or contains(text(), "Okay")]')))
    print("Pop-up de cookies encontrado. Fechando...")
    cookie_button.click()
    time.sleep(2)
except TimeoutException:
    print("Nenhum pop-up de cookies encontrado. Continuando...")

# Bloco ATUALIZADO com JavaScript Click para o pop-up de Idiomas
try:
    seletor_botao_fechar_idiomas = "div[role='dialog'][aria-label='Idiomas'] button[aria-label='Fechar']"
    botao_fechar = wait_popup.until(EC.presence_of_element_located((By.CSS_SELECTOR, seletor_botao_fechar_idiomas)))
    print("Pop-up de 'Idiomas' encontrado. Fechando via JavaScript...")
    driver.execute_script("arguments[0].click();", botao_fechar)
    time.sleep(2)
except TimeoutException:
    print("Nenhum pop-up de 'Idiomas' encontrado. Continuando...")


# Aguardar o carregamento dos anúncios na página principal
try:
    print("Aguardando os anúncios carregarem na página principal...")
    anuncio_selector = (By.CSS_SELECTOR, "[data-testid='card-container']")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(anuncio_selector))
    print("Anúncios carregados.")
except TimeoutException:
    print("ERRO: Os cards de anúncio não carregaram a tempo.")
    driver.quit()
    exit()

# Encontrar os anúncios e iniciar o loop de extração ---
elements = driver.find_elements(By.CSS_SELECTOR, "[data-testid='card-container']")
if not elements:
    print("Nenhum anúncio encontrado. O script será encerrado.")
    driver.quit()
    exit()

dados_airbnb = []
NUMERO_DE_ANUNCIOS = 3
print(f"\nEncontrados {len(elements)} anúncios. Processando os {NUMERO_DE_ANUNCIOS} primeiros para teste...")
count = 0 

for element in elements:
    if count >= NUMERO_DE_ANUNCIOS:
        print(f"\nLimite de {NUMERO_DE_ANUNCIOS} anúncios atingido para este teste.")
        break
    
    link = "Não encontrado"
    try:
        link_element = element.find_element(By.TAG_NAME, "a")
        link = link_element.get_attribute('href')

        driver.execute_script("window.open(arguments[0], '_blank');", link)
        driver.switch_to.window(driver.window_handles[1])

        try:
            wait_rapido = WebDriverWait(driver, 5)
            wait_rapido.until(EC.visibility_of_element_located((By.XPATH, "//h1[text()='Tradução ativada']")))
            
            print("Tela 'Tradução ativada' detectada. Fechando...")
            botao_continuar = driver.find_element(By.XPATH, "//h1[text()='Tradução ativada']/following::button[1]")
            botao_continuar.click()
            time.sleep(2)
        except TimeoutException:
            pass
        except Exception as e:
            print(f"Não foi possível fechar a tela de tradução: {e}")

        try:
            wait_details = WebDriverWait(driver, 20)
            
            nome_anuncio = "Não encontrado"
            media_avaliacoes = "Não encontrada"
            total_avaliacoes = "Não encontrado"
            localizacao = "Não encontrada"
            dias_disponiveis = "Nenhum encontrado"

            try:
                nome_anuncio_selector = (By.CSS_SELECTOR, "h1")
                nome_element = wait_details.until(EC.visibility_of_element_located(nome_anuncio_selector))
                nome_anuncio = nome_element.text
            except TimeoutException:
                print(f"AVISO: Nome do anúncio não encontrado para o link: {link}")

            try:
                driver.execute_script("window.scrollBy(0, 400);")
                time.sleep(1)
                avaliacoes_selector = (By.XPATH, "//a[contains(., 'avaliaç')] | //button[contains(., 'avaliaç')]")
                avaliacoes_element = wait_details.until(EC.visibility_of_element_located(avaliacoes_selector))
                texto_completo_avaliacoes = avaliacoes_element.text
                if '·' in texto_completo_avaliacoes:
                    partes = texto_completo_avaliacoes.split('·')
                    media_avaliacoes = "★ " + partes[0].strip()
                    total_avaliacoes = partes[1].strip()
                elif texto_completo_avaliacoes:
                    total_avaliacoes = texto_completo_avaliacoes
            except TimeoutException:
                print(f"AVISO: Nenhuma avaliação encontrada ou não carregou a tempo para o link: {link}")

            try:
                localizacao_selector = (By.CSS_SELECTOR, "[data-testid='listing-map-button']")
                localizacao_element = wait_details.until(EC.visibility_of_element_located(localizacao_selector))
                localizacao = localizacao_element.text
            except TimeoutException:
                print(f"AVISO: Localização não encontrada ou não carregou a tempo para o link: {link}")
            
            try:
                available_day_elements = driver.find_elements(By.CSS_SELECTOR, "div[data-is-day-blocked='false']")
                
                lista_datas = []
                for day_element in available_day_elements:
                    testid = day_element.get_attribute('data-testid')
                    data = testid.replace('calendar-day-', '')
                    lista_datas.append(data)
                
                if lista_datas:
                    dias_disponiveis = "; ".join(lista_datas)
            except Exception as e:
                print(f"AVISO: Não foi possível extrair os dias disponíveis - {e}")

            
            print("---------------------------------")
            print(f"Coletado: {nome_anuncio}")

            dados_airbnb.append({
                'Nome do Anuncio': nome_anuncio,
                'Nota Media': media_avaliacoes,
                'Total de Avaliacoes': total_avaliacoes,
                'Localizacao': localizacao,
                'Dias Disponiveis': dias_disponiveis,
                'Link': link
            })

        except Exception as e:
            print(f"ERRO inesperado ao processar detalhes da página: {link} - Erro: {e}")
        finally:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

    except Exception as e:
        print(f"Erro inesperado no loop principal ao processar um elemento: {e}")
    
    count += 1

# Salvar os dados em um arquivo .txt ---
print("\nColeta finalizada. Salvando dados em arquivo de texto...")
try:
    with open('hospedagens.txt', 'w', encoding='utf-8') as f:
        if not dados_airbnb:
            f.write("Nenhum dado de hospedagem foi coletado.")
        else:
            for anuncio in dados_airbnb:
                f.write(f"Nome do Anuncio: {anuncio.get('Nome do Anuncio', 'N/A')}\n")
                f.write(f"Nota Media: {anuncio.get('Nota Media', 'N/A')}\n")
                f.write(f"Total de Avaliacoes: {anuncio.get('Total de Avaliacoes', 'N/A')}\n")
                f.write(f"Localizacao: {anuncio.get('Localizacao', 'N/A')}\n")
                f.write(f"Dias Disponiveis: {anuncio.get('Dias Disponiveis', 'N/A')}\n")
                f.write(f"Link: {anuncio.get('Link', 'N/A')}\n")
                f.write("--------------------------------------------------\n")
    print("Arquivo 'hospedagens.txt' salvo com sucesso!")
except Exception as e:
    print(f"ERRO ao salvar o arquivo .txt: {e}")

# Encerrar o navegador
driver.quit()