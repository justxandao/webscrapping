import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

# CONEXÃO COM O DATA WAREHOUSE NO DOCKER

db_user = 'docker'
db_password = 'docker'
db_host = 'localhost'
db_port = '5439'
db_name = 'pixtur_dw'

db_connection_str = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

try:
    db_engine = create_engine(db_connection_str)
    print("Conexão com o Data Warehouse bem-sucedida!")
except Exception as e:
    print(f"Erro ao conectar ao Data Warehouse: {e}")
    exit()

# EXTRAÇÃO DOS DADOS VIA SQL
# ====================================================================
sql_query = """
SELECT
    fh.preco_diaria,
    fh.qtd_avaliacoes,
    fh.nota_media,
    dl.cidade,
    dh.nome,
    dh.tipo,
    -- Cria a coluna 'ano_mes' para o gráfico de evolução
    TO_CHAR(dt.data_completa, 'YYYY-MM') as ano_mes
FROM
    Fato_Hospedagem fh
JOIN
    Dim_Localizacao dl ON fh.fk_local = dl.sk_local
JOIN
    Dim_Hotel dh ON fh.fk_hotel = dh.sk_hotel
JOIN
    Dim_Tempo dt ON fh.fk_tempo = dt.sk_tempo;
"""

print("Buscando dados do Data Warehouse...")
df_completo = pd.read_sql(sql_query, db_engine)
print("Dados carregados com sucesso!")

sns.set_theme(style="whitegrid")

# --- GRÁFICO 1: Comparação de preços médios por cidade ---
print("\nGerando Gráfico 1: Preços médios por cidade...")
df_preco_cidade = df_completo.groupby('cidade')['preco_diaria'].mean().sort_values(ascending=False).reset_index()

plt.figure(figsize=(12, 7))
ax1 = sns.barplot(x='cidade', y='preco_diaria', data=df_preco_cidade, palette='viridis')
ax1.set_title('Comparação de Preços Médios por Diária por Cidade', fontsize=16)
ax1.set_xlabel('Cidade', fontsize=12)
ax1.set_ylabel('Preço Médio da Diária (R$)', fontsize=12)
plt.tight_layout()
plt.show()

# GRÁFICO 2: Relação entre número de avaliações e nota média
print("\nGerando Gráfico 2: Relação entre Nº de Avaliações e Nota Média...")
plt.figure(figsize=(10, 6))
ax2 = sns.scatterplot(x='qtd_avaliacoes', y='nota_media', data=df_completo, hue='cidade', s=100, alpha=0.8)
ax2.set_title('Relação entre Número de Avaliações e Nota Média', fontsize=16)
ax2.set_xlabel('Quantidade de Avaliações', fontsize=12)
ax2.set_ylabel('Nota Média (0 a 10)', fontsize=12)
plt.legend(title='Cidade')
plt.tight_layout()
plt.show()

# GRÁFICO 3: Distribuição de tipos de hospedagem por cidade
print("\nGerando Gráfico 3: Distribuição de Tipos de Hospedagem...")
plt.figure(figsize=(12, 7))
ax3 = sns.countplot(data=df_completo, x='cidade', hue='tipo', palette='plasma')
ax3.set_title('Distribuição de Tipos de Hospedagem por Cidade', fontsize=16)
ax3.set_xlabel('Cidade', fontsize=12)
ax3.set_ylabel('Quantidade de Opções', fontsize=12)
plt.tight_layout()
plt.show()

# GRÁFICO 4: Evolução do preço de hospedagens ao longo do tempo
print("\nGerando Gráfico 4: Evolução de Preços ao Longo do Tempo...")
df_preco_tempo = df_completo.groupby('ano_mes')['preco_diaria'].mean().reset_index()

plt.figure(figsize=(12, 6))
ax4 = sns.lineplot(x='ano_mes', y='preco_diaria', data=df_preco_tempo, marker='o', sort=False)
ax4.set_title('Evolução do Preço Médio das Hospedagens ao Longo do Tempo', fontsize=16)
ax4.set_xlabel('Ano-Mês', fontsize=12)
ax4.set_ylabel('Preço Médio da Diária (R$)', fontsize=12)
plt.tight_layout()
plt.show()

# GRÁFICO 5: Ranking das hospedagens mais bem avaliadas por região
print("\nGerando Gráfico 5: Ranking das Melhores Hospedagens...")
cidade_escolhida = 'Salvador'

df_cidade_filtrada = df_completo[df_completo['cidade'] == cidade_escolhida]
df_ranking = df_cidade_filtrada.sort_values(by='nota_media', ascending=False).head(10)

plt.figure(figsize=(12, 8))
ax5 = sns.barplot(x='nota_media', y='nome', data=df_ranking, palette='coolwarm')
ax5.set_title(f'Top Hospedagens Mais Bem Avaliadas em {cidade_escolhida}', fontsize=16)
ax5.set_xlabel('Nota Média', fontsize=12)
ax5.set_ylabel('Hospedagem', fontsize=12)
ax5.set_xlim(left=7.5, right=10)
plt.tight_layout()
plt.show()