# %%
import pandas as pd
import streamlit as st
import os


# %%

# Databases: criando os objetos

# Criando os objetos para cada banco de dados
# latin1 é usado para que caracteres epeciais como 'ç' ou '~' não quebrem na hora
# da leitura.

path = "databases/"
skip_counts = {}

def carregar_com_checkpoint(nome_arquivo, sep=','):
    full_path = os.path.join(path, nome_arquivo)
    
    # Contagem inicial de linhas no arquivo físico
    with open(full_path, 'r', encoding='latin1') as f:
        linhas_arquivo = sum(1 for line in f)
    
    df = pd.read_csv(
        full_path, 
        sep=sep, 
        encoding='latin1', 
        on_bad_lines='skip', 
        low_memory=False
    )
    
    # Checkpoint de carga
    linhas_carregadas = len(df)
    linhas_skipadas = linhas_arquivo - linhas_carregadas - 1 # -1 pelo header
    skip_counts[nome_arquivo] = linhas_skipadas
    
    print(f"--- Checkpoint: {nome_arquivo} ---")
    print(f"Linhas no arquivo: {linhas_arquivo}")
    print(f"Linhas carregadas: {linhas_carregadas}")
    print(f"Linhas SKIPADAS (erro de formatação): {linhas_skipadas}\n")
    
    return df

# Carga respeitando os separadores específicos
df_alvara = carregar_com_checkpoint("1.CM_Alvara_de_Pesquisa.csv", sep=',')
df_lavra = carregar_com_checkpoint("1.CM_Portaria_de_Lavra.csv", sep=',')
df_arrecadacao = carregar_com_checkpoint("2.CFEM_Arrecadacao_2022_2026.csv", sep=',')
df_distribuicao = carregar_com_checkpoint("2.CFEM_Distribuicao.csv", sep=',')
df_barragens = carregar_com_checkpoint("3.SIGBM_(Barragens).csv", sep=',')

# Separador ';' para estes dois conforme seu aviso
df_divida = carregar_com_checkpoint("4.DividaATIVA_Procuradoria_DividaAtiva.csv", sep=';')
df_sople = carregar_com_checkpoint("5.SOPLE-Leilao_EstoqueAreas.csv", sep=';')

# %%

# Check dos headings
import sys

# Nome do arquivo de log
log_file = "databases/databases_log.txt"

# Certificando que a pasta 'data' existe
if not os.path.exists('data'):
    os.makedirs('data')

with open(log_file, "w", encoding="utf-8") as f:
    # Redireciona a saída do sistema para o arquivo temporariamente
    sys.stdout = f
    
    print("=== LOG DE ESTRUTURA DOS BANCOS DE DATOS - STARTMINE ===")
    print(f"Data do Log: {pd.Timestamp.now()}\n")
    
    print("--- 1. ALVARÁ DE PESQUISA ---")
    print(df_alvara.head(1))
    print("\n")
    
    print("--- 1. PORTARIA DE LAVRA ---")
    print(df_lavra.head(1))
    print("\n")
    
    print("--- 2. CFEM ARRECADAÇÃO ---")
    print(df_arrecadacao.head(1))
    print("\n")
    
    print("--- 2. CFEM DISTRIBUIÇÃO ---")
    print(df_distribuicao.head(1))
    print("\n")
    
    print("--- 3. SIGBM (BARRAGENS) ---")
    print(df_barragens.head(1))
    print("\n")
    
    print("--- 4. DÍVIDA ATIVA ---")
    print(df_divida.head(1))
    print("\n")
    
    print("--- 5. SOPLE (LEILÃO) ---")
    print(df_sople.head(1))
    print("\n")
    
    # Restaura a saída para o terminal
    sys.stdout = sys.__stdout__

print(f"✅ Log salvo com sucesso em: {log_file}")





# %%

# Limpeza: extraindo informações das empresas no Vale do Lítio

vale_litio = [
    'ARAÇUAÍ', 'CAPELINHA', 'CORONEL MURTA', 'ITAOBIM', 'ITINGA', 
    'MALACACHETA', 'MEDINA', 'MINAS NOVAS', 'PEDRA AZUL', 
    'VIRGEM DA LAPA', 'TEÓFILO OTONI', 'TURMALINA', 'RUBELITA', 'SALINAS'
]


# %%
log_file = "databases/databases_log.txt"

def filtrar_com_log(df, nome_base, coluna_mun):
    antes = len(df)
    
    # 1. Tratamento robusto: Upper + Split no '-' para remover o UF (ex: ITINGA - MG)
    df[coluna_mun] = df[coluna_mun].astype(str).str.split('-').str[0].str.strip().str.upper()
    
    # 2. Execução do Filtro pelo Vale do Lítio
    df_filtrado = df[df[coluna_mun].isin(vale_litio)].copy()
    depois = len(df_filtrado)
    
    # 3. Preparando a mensagem de log
    status = "SUCESSO" if depois > 0 else "ALERTA: ZERO RESULTADOS"
    log_msg = (
        f"--- Filtro Vale do Lítio: {nome_base} ---\n"
        f"Status: {status}\n"
        f"Registros ANTES: {antes}\n"
        f"Registros DEPOIS: {depois}\n"
        f"Redução: {((antes-depois)/antes)*100 if antes > 0 else 0:.2f}%\n\n"
    )
    
    # Exibe no console para você acompanhar a "fritação"
    print(log_msg)
    
    # Salva no arquivo (modo 'a' de append para não apagar o head que você já salvou)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_msg)
        
    return df_filtrado


# %%
# Correção manual do nome da coluna do SOPLE se houver o caractere estranho
if 'ï»¿ProcessoMinerario' in df_sople.columns:
    df_sople = df_sople.rename(columns={'ï»¿ProcessoMinerario': 'ProcessoMinerario'})


# %%
# --- Execução da Limpeza ---

# Adiciona um cabeçalho de seção no log
with open(log_file, "a", encoding="utf-8") as f:
    f.write("\n=== CHECKPOINT DE LIMPEZA GEOGRÁFICA (VALE DO LÍTIO) ===\n")
    f.write(f"Executado em: {pd.Timestamp.now()}\n\n")

# Aplicando os filtros conforme as colunas exatas do seu LOG anterior
df_alvara_v = filtrar_com_log(df_alvara, "Cadastro (Alvará)", "Municipio(s)")
df_lavra_v = filtrar_com_log(df_lavra, "Cadastro (Lavra)", "Municipio(s)")
df_barragens_v = filtrar_com_log(df_barragens, "Barragens (SIGBM)", "Município")
df_arrecadacao_v = filtrar_com_log(df_arrecadacao, "CFEM Arrecadação", "Município")
df_distribuicao_v = filtrar_com_log(df_distribuicao, "CFEM Distribuição", "NomeEnte")
df_sople_v = filtrar_com_log(df_sople, "SOPLE (Leilão)", "Municipio")
# note que não há como filtrar pela dívida pois a dívida temos somente CNPJ e 
    # parte do CPF como identificador.

print(f"✅ Processo concluído! O log detalhado está em: {log_file}")



# %%

with open(log_file, "a", encoding="utf-8") as f:
    # Redireciona a saída do sistema para o arquivo temporariamente
    sys.stdout = f
    
    print("=== ESTRUTURA APÓS A LIMPEZA PARA VALE DO LÍTIO - STARTMINE ===")
    print(f"Data do Log: {pd.Timestamp.now()}\n")
    
    print("--- 1. ALVARÁ DE PESQUISA ---")
    print(df_alvara_v.head(1))
    print("\n")
    
    print("--- 1. PORTARIA DE LAVRA ---")
    print(df_lavra_v.head(1))
    print("\n")
    
    print("--- 2. CFEM ARRECADAÇÃO ---")
    print(df_arrecadacao_v.head(1))
    print("\n")
    
    print("--- 2. CFEM DISTRIBUIÇÃO ---")
    print(df_distribuicao_v.head(1))
    print("\n")
    
    print("--- 3. SIGBM (BARRAGENS) ---")
    print(df_barragens.head(1))
    print("\n")
    
    print("--- 4. DÍVIDA ATIVA ---")
    print(df_divida.head(1))
    print("\n")
    
    print("--- 5. SOPLE (LEILÃO) ---")
    print(df_sople.head(1))
    print("\n")
    
    # Restaura a saída para o terminal
    sys.stdout = sys.__stdout__

print(f"✅ Log salvo com sucesso em: {log_file}")



# %%

# Padronizando os CNPJs

import re

def limpar_documento(doc):
    """Remove pontuação e espaços de CPFs/CNPJs."""
    if pd.isna(doc): return ""
    return re.sub(r'\D', '', str(doc)) # Remove tudo que não for número

# 1. Padronizando o Cadastro (Alvará e Lavra)
df_alvara_v['doc_limpo'] = df_alvara_v['CPF/CNPJ do titular'].apply(limpar_documento)
df_lavra_v['doc_limpo'] = df_lavra_v['CPF/CNPJ do titular'].apply(limpar_documento)

# 2. Padronizando a Dívida Ativa
df_divida['doc_limpo'] = df_divida['CPF_CNPJ'].apply(limpar_documento)



# %%
# 1. Padronização de Documentos (CNPJ/CPF) em todas as bases relevantes
df_alvara_v['doc_limpo'] = df_alvara_v['CPF/CNPJ do titular'].apply(limpar_documento)
df_lavra_v['doc_limpo'] = df_lavra_v['CPF/CNPJ do titular'].apply(limpar_documento)
df_arrecadacao_v['doc_limpo'] = df_arrecadacao_v['CPF_CNPJ'].apply(limpar_documento)
df_barragens_v['doc_limpo'] = df_barragens_v['CPF_CNPJ'].apply(limpar_documento)
df_divida['doc_limpo'] = df_divida['CPF_CNPJ'].apply(limpar_documento)

# %%
# 2. Cruzamento específico para Dívida Ativa (Filtrando apenas devedores do Vale)
docs_vale = pd.concat([
    df_alvara_v['doc_limpo'], 
    df_lavra_v['doc_limpo'],
    df_arrecadacao_v['doc_limpo']
]).unique()

df_divida_vale = df_divida[df_divida['doc_limpo'].isin(docs_vale)].copy()

# %%
# 3. Salvamento Individual das 7 Bases
df_alvara_v.to_csv('databases/dashboard/1.dashboard_CM_alvara.csv', index=False)
df_lavra_v.to_csv('databases/dashboard/1.dashboard_CM_lavra.csv', index=False)
df_arrecadacao_v.to_csv('databases/dashboard/2.dashboard_cefem_arrecadacao.csv', index=False)
df_distribuicao_v.to_csv('databases/dashboard/2.dashboard_cefem_distribuicao.csv', index=False)
df_barragens_v.to_csv('databases/dashboard/3.dashboard_sigbm_barragens.csv', index=False)
df_divida_vale.to_csv('databases/dashboard/4.dashboard_divida_ativa.csv', index=False)
df_sople_v.to_csv('databases/dashboard/5.dashboard_sople.csv', index=False)

# %%
# 4. Log de Finalização
log_final = (
    f"\n=== FRITAÇÃO CONCLUÍDA: 7 BASES GERADAS ===\n"
    f"1. Alvará: {len(df_alvara_v)} registros\n"
    f"2. Lavra: {len(df_lavra_v)} registros\n"
    f"3. Arrecadação: {len(df_arrecadacao_v)} registros\n"
    f"4. Distribuição: {len(df_distribuicao_v)} registros\n"
    f"5. Barragens: {len(df_barragens_v)} registros\n"
    f"6. Dívida Ativa (Vale): {len(df_divida_vale)} registros\n"
    f"7. SOPLE: {len(df_sople_v)} registros\n"
)

print(log_final)
with open(log_file, "a", encoding="utf-8") as f:
    f.write(log_final)

print("🚀 7 bancos de dados prontos individualmente!")

# %%

cam = pd.read_csv('databases/dashboard/1.dashboard_CM_lavra.csv')
empresas = cam['titular']