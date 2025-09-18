import requests
from bs4 import BeautifulSoup
import time
import random
import json

# Simulação da extração de dados de produtos
def extrair_pagina(url):
    """
    Faz a requisição HTTP, analisa o HTML e extrai os dados de produtos.
    """
    try:
        # Fazer a requisição HTTP para a URL
        response = requests.get(url)
        # Verificar se a requisição foi bem-sucedida (código 200)
        response.raise_for_status()
        
        # Analisar o conteúdo HTML da página
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Encontrar todas as 'divs' que representam um produto/citação
        quotes = soup.find_all('div', class_='quote')
        
        dados_produtos = []
        for quote in quotes:
            # Extrair os dados de cada produto
            nome_produto = quote.find('span', class_='text').text.strip()
            autor_marca = quote.find('small', class_='author').text.strip()
            tags = [tag.text for tag in quote.find('div', class_='tags').find_all('a', class_='tag')]

            # Gerar dados fictícios
            preco_ficticio = round(random.uniform(10.00, 500.00), 2)
            avaliacao_ficticia = round(random.uniform(1.0, 5.0), 1)
            
            # Adicionar os dados em um dicionário
            dados_produtos.append({
                "nome_produto": nome_produto,
                "autor_marca": autor_marca,
                "tags_categoria": tags,
                "preco_ficticio": preco_ficticio,
                "avaliacao_ficticia": avaliacao_ficticia,
                "data_da_extracao": time.strftime("%Y-%m-%d %H:%M:%S")
            })
            
        return dados_produtos

    except requests.exceptions.RequestException as e:
        print(f"Erro ao fazer a requisição para {url}: {e}")
        return None

# --- Código para testar a extração de uma única página ---
if __name__ == "__main__":
    url_teste = "https://quotes.toscrape.com/"
    print(f"Testando a extração da página: {url_teste}\n")
    
    dados_extraidos = extrair_pagina(url_teste)
    
    if dados_extraidos:
        print(f"Dados extraídos com sucesso. Foram encontrados {len(dados_extraidos)} produtos.\n")
        # Imprime os dados para visualização
        for i, produto in enumerate(dados_extraidos):
            print(f"--- Produto {i+1} ---")
            print(f"Nome: {produto['nome_produto']}")
            print(f"Autor: {produto['autor_marca']}")
            print(f"Preço Fictício: R${produto['preco_ficticio']:.2f}")
            print(f"Avaliação Fictícia: {produto['avaliacao_ficticia']}")
            print("-" * 20)
    else:
        print("Não foi possível extrair os dados. Verifique a URL e a conexão.")