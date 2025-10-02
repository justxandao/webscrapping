import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

data_fato = {
    'fk_local': [1, 1, 1, 2, 2, 2, 3, 3, 3],
    'fk_hotel': [101, 102, 101, 103, 105, 103, 104, 106, 107],
    'fk_tempo': [201, 202, 203, 201, 202, 203, 201, 202, 203],
    'preco_diaria': [1500.00, 350.50, 1650.00, 420.00, 210.00, 450.00, 890.00, 150.00, 600.00],
    'qtd_avaliacoes': [2500, 450, 2510, 120, 800, 125, 1800, 300, 85],
    'nota_media': [9.8, 8.5, 9.8, 9.2, 7.8, 9.3, 8.9, 8.0, 9.5]
}
df_fato = pd.DataFrame(data_fato)

data_local = {
    'sk_local': [1, 2, 3],
    'cidade': ['Rio de Janeiro', 'São Paulo', 'Salvador']
}
df_local = pd.DataFrame(data_local)

data_hotel = {
    'sk_hotel': [101, 102, 103, 104, 105, 106, 107],
    'nome': ['Copacabana Palace', 'Pousada Mar e Sol', 'Apartamento Moderno Av. Paulista', 'Grand Hotel Stella Maris', 'Ibis Budget SP', 'Hostel da Vila', 'Casa com Piscina no Pelourinho'],
    'tipo': ['Hotel', 'Pousada', 'Aluguel por temporada', 'Resort', 'Hotel', 'Pousada', 'Aluguel por temporada']
}
df_hotel = pd.DataFrame(data_hotel)

data_tempo = {
    'sk_tempo': [201, 202, 203],
    'ano_mes': ['2025-08', '2025-09', '2025-10']
}
df_tempo = pd.DataFrame(data_tempo)

sns.set_theme(style="whitegrid")

df_completo = pd.merge(df_fato, df_local, left_on='fk_local', right_on='sk_local')
df_completo = pd.merge(df_completo, df_hotel, left_on='fk_hotel', right_on='sk_hotel')
df_completo = pd.merge(df_completo, df_tempo, left_on='fk_tempo', right_on='sk_tempo')


print("\nGerando Gráfico 1: Preços médios por cidade...")
df_preco_cidade = df_completo.groupby('cidade')['preco_diaria'].mean().sort_values(ascending=False).reset_index()

plt.figure(figsize=(12, 7))
ax1 = sns.barplot(x='cidade', y='preco_diaria', data=df_preco_cidade, palette='viridis')
ax1.set_title('Comparação de Preços Médios por Diária por Cidade', fontsize=16)
ax1.set_xlabel('Cidade', fontsize=12)
ax1.set_ylabel('Preço Médio da Diária (R$)', fontsize=12)
plt.tight_layout()
plt.show()

print("""
**Interpretação - Gráfico 1:**
Este gráfico de barras compara o custo médio de uma diária nas diferentes cidades.
Ele permite identificar rapidamente o Rio de Janeiro como a cidade com a diária média mais cara
em nosso conjunto de dados, seguido por Salvador e São Paulo.
""")


print("\nGerando Gráfico 2: Relação entre Nº de Avaliações e Nota Média...")
plt.figure(figsize=(10, 6))
ax2 = sns.scatterplot(x='qtd_avaliacoes', y='nota_media', data=df_completo, hue='cidade', s=100, alpha=0.8)
ax2.set_title('Relação entre Número de Avaliações e Nota Média', fontsize=16)
ax2.set_xlabel('Quantidade de Avaliações', fontsize=12)
ax2.set_ylabel('Nota Média (0 a 10)', fontsize=12)
plt.legend(title='Cidade')
plt.tight_layout()
plt.show()

print("""
**Interpretação - Gráfico 2:**
Este gráfico de dispersão mostra que não há uma correlação clara e linear entre quantidade de
avaliações e nota. Notamos, por exemplo, a hospedagem com mais avaliações (Copacabana Palace)
também possui a nota mais alta, mas outras com poucas avaliações também atingem notas excelentes.
""")


print("\nGerando Gráfico 3: Distribuição de Tipos de Hospedagem...")
plt.figure(figsize=(12, 7))
ax3 = sns.countplot(data=df_completo, x='cidade', hue='tipo', palette='plasma')
ax3.set_title('Distribuição de Tipos de Hospedagem por Cidade', fontsize=16)
ax3.set_xlabel('Cidade', fontsize=12)
ax3.set_ylabel('Quantidade de Opções', fontsize=12)
plt.tight_layout()
plt.show()

print("""
**Interpretação - Gráfico 3:**
Este gráfico mostra a composição da oferta de hospedagem. Em nossos dados,
cada cidade possui uma oferta variada, com hotéis, pousadas e outras modalidades.
São Paulo se destaca pela presença de hotéis, enquanto Salvador mostra uma boa
variedade, incluindo aluguel por temporada.
""")


print("\nGerando Gráfico 4: Evolução de Preços ao Longo do Tempo...")
df_preco_tempo = df_completo.groupby('ano_mes')['preco_diaria'].mean().reset_index()

plt.figure(figsize=(12, 6))
ax4 = sns.lineplot(x='ano_mes', y='preco_diaria', data=df_preco_tempo, marker='o', sort=False)
ax4.set_title('Evolução do Preço Médio das Hospedagens ao Longo do Tempo', fontsize=16)
ax4.set_xlabel('Ano-Mês', fontsize=12)
ax4.set_ylabel('Preço Médio da Diária (R$)', fontsize=12)
plt.tight_layout()
plt.show()

print("""
**Interpretação - Gráfico 4:**
O gráfico de linhas demonstra uma tendência de alta nos preços médios de agosto para outubro.
Isso pode indicar o início de uma alta temporada ou uma recuperação de preços no mercado,
uma informação crucial para a estratégia da PixTur.
""")


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

print(f"""
**Interpretação - Gráfico 5:**
Este ranking horizontal destaca as melhores opções em {cidade_escolhida} com base na satisfação
do cliente. A 'Casa com Piscina no Pelourinho' lidera, mostrando que nem sempre as
opções mais tradicionais como resorts são as mais bem avaliadas.
""")