import streamlit as st
import pandas as pd
import plotly.express as px
import os

# %% Configuração da página
st.set_page_config(page_title="StratMine | Inteligência Mineral", layout="wide")

<<<<<<< HEAD
# --- DEFINIÇÃO DE CAMINHOS ---
=======
# --- DEFINIÇÃO DE CAMINHOS (O segredo para funcionar na nuvem) ---
>>>>>>> 0c7f9e15993810a540eb7463929da55c7d9f5446
# Pega o caminho da pasta onde o app.py está
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- CARGA DE DADOS ---
@st.cache_data
def load_data():
    # Usamos o BASE_DIR para o Python saber exatamente onde está a pasta databases
    df_alvara = pd.read_csv(os.path.join(BASE_DIR, 'databases', '1.dashboard_CM_alvara.csv'))
    df_lavra = pd.read_csv(os.path.join(BASE_DIR, 'databases', '1.dashboard_CM_lavra.csv'))
    df_arr = pd.read_csv(os.path.join(BASE_DIR, 'databases', '2.dashboard_cefem_arrecadacao.csv'))
    df_bar = pd.read_csv(os.path.join(BASE_DIR, 'databases', '3.dashboard_sigbm_barragens.csv'))
    df_div = pd.read_csv(os.path.join(BASE_DIR, 'databases', '4.dashboard_divida_ativa.csv'))
    
    return df_alvara, df_lavra, df_arr, df_bar, df_div

# Chamada única da função (Remova a segunda definição de load_data que você tinha)
df_alvara, df_lavra, df_arr, df_bar, df_div = load_data()

# %%
 # --- TÍTULO ---

st.title("StratMine - Inteligência Mineral")

st.markdown(f"**Região:** Vale do Lítio (MG) | **Data de atualização:** 03/05/2026")


# %% BARRA LATERAL E NAVEGAÇÃO
with st.sidebar:
    st.markdown("# **STRATMINE**")
    st.markdown("### Inteligência Mineral")
    st.divider()
    
    aba_selecionada = st.radio(
        "Navegação",
        ["Panorama Geral", "Panorama por Município", "Panorama por Substância", "Panorama das Empresas"]
    )

# %% CONTEÚDO DAS ABAS

# ------------ PANORAMA POR GERAL


if aba_selecionada == "Panorama Geral":

    # --- BLOCO SUPERIOR (Texto 2 e Métricas) ---
    col_texto, col_metrics = st.columns([1.5, 1])
    
    with col_texto:
        st.info("O Vale do Lítio é uma região estratégica no Norte e Nordeste de Minas Gerais (Vale do" 
                    "Jequitinhonha/Mucuri) com uma das maiores reservas de lítio do mundo. O" 
                    "projeto estadual, focado na transição energética, atraiu mais de R$ 6 " 
                    "bilhões em investimentos, gerando cerca de 4.000 empregos em 14 " 
                    "municípios.\n" \
                    "\nTodos os dados aqui representados foram gerados"
                    "a partir de dados da ANM - Agencia Nacional de Mineração.")
        
    with col_metrics:
        # Cálculo de métricas
        n_municipios = 14 # Conforme sua lista vale_litio
        # Número de empresas únicas lavrando no Vale
        n_empresas_lavra = df_lavra['doc_limpo'].nunique()
        
        st.metric("Nº de Municípios no Vale do Lítio", n_municipios)
        st.metric("Nº de Empresas Lavrando", n_empresas_lavra)

    st.divider()

    # --- BLOCO INFERIOR (Gráficos) ---
 
    
    # --- GRÁFICO 1 (LAVRA X PESQUISA) ---
    st.markdown("### LAVRA x PESQUISA")

    # Contagem por município em cada base
    count_pesquisa = df_alvara.groupby('Municipio(s)').size().reset_index(name='Pesquisa')
    count_lavra = df_lavra.groupby('Municipio(s)').size().reset_index(name='Lavra')

    # Merge para cruzar as informações
    df_barras = pd.merge(count_pesquisa, count_lavra, on='Municipio(s)', how='outer').fillna(0)

    # Criando o gráfico de barras duplas (barmode='group' coloca as barras lado a lado)
    fig_comparativo = px.bar(
        df_barras,
        x="Municipio(s)",
        y=["Lavra", "Pesquisa"],
        barmode="group",
        labels={"value": "Quantidade de Processos", "variable": "Tipo", "Municipio(s)": "Cidade"},
        color_discrete_map={"Pesquisa": "red", "Lavra": "green"}, # Cores seguindo seu esboço
        template="plotly_white"
    )

    # Ajustes de Layout
    fig_comparativo.update_layout(
        yaxis_title=None, # Remove a régua/título do lado esquerdo
        legend_title_text='Fase do Processo',
        legend=dict(
            orientation="h", # Legenda horizontal
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    st.plotly_chart(fig_comparativo, use_container_width=True)




      # --- GRÁFICO 2 (LAVRA & PESQUISA X TEMPO) ---
    st.markdown("### LAVRA & PESQUISA x TEMPO")

    # 1. Extraindo o ano do processo e garantindo que sejam inteiros
    df_alvara['Ano'] = df_alvara['Processo'].str.split('/').str[-1].astype(int)
    df_lavra['Ano'] = df_lavra['Processo'].str.split('/').str[-1].astype(int)

    # 2. Agrupando por ano
    time_pesquisa = df_alvara.groupby('Ano').size().reset_index(name='Pesquisa')
    time_lavra = df_lavra.groupby('Ano').size().reset_index(name='Lavra')

    # 3. Merge inicial e filtro de anos
    df_tempo_bruto = pd.merge(time_pesquisa, time_lavra, on='Ano', how='outer').fillna(0)
    df_tempo_bruto = df_tempo_bruto[df_tempo_bruto['Ano'] >= 1930].sort_values('Ano')

    if not df_tempo_bruto.empty:
        # 4. Criar range completo de anos para evitar as linhas retas entre anos sem dados
        ano_min_geral = int(df_tempo_bruto['Ano'].min())
        ano_max_geral = int(df_tempo_bruto['Ano'].max())
        todos_anos_geral = pd.DataFrame({'Ano': range(ano_min_geral, ano_max_geral + 1)})

        # 5. Reindexar para preencher anos vazios com 0
        df_tempo_final = pd.merge(todos_anos_geral, df_tempo_bruto, on='Ano', how='left').fillna(0)

        # 6. Gerar o gráfico de linha
        fig_tempo = px.line(
            df_tempo_final, 
            x="Ano", 
            y=["Pesquisa", "Lavra"],
            color_discrete_map={"Pesquisa": "red", "Lavra": "green"},
            labels={"value": "Total de Processos", "variable": "Fase"},
            template="plotly_white",
            markers=True # Adiciona as bolinhas
        )

        # Deixar as linhas tracejadas
        fig_tempo.update_traces(line=dict(dash='dash'))

        fig_tempo.update_layout(
            xaxis_title="Ano do Processo",
            yaxis_title=None,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        st.plotly_chart(fig_tempo, use_container_width=True)
    else:
        st.info("Dados insuficientes para gerar a linha do tempo histórica.")



# ==============================================================================
# ABA: PANORAMA POR MUNICÍPIOS
# ==============================================================================


elif aba_selecionada == "Panorama por Município":
    st.title("📍 Detalhamento por Município")

    vale_litio = [
        'ARAÇUAÍ', 'CAPELINHA', 'CORONEL MURTA', 'ITAOBIM', 'ITINGA', 
        'MALACACHETA', 'MEDINA', 'MINAS NOVAS', 'PEDRA AZUL', 
        'VIRGEM DA LAPA', 'TEÓFILO OTONI', 'TURMALINA', 'RUBELITA', 'SALINAS'
    ]

    # 1. Seletor de Cidade (O "clique" que ativa as informações)
    cidade_selecionada = st.selectbox(
        "Selecione uma cidade para ver o detalhamento estratégico:",
        options=sorted(vale_litio)
    )

    st.divider()

    # 2. Filtragem dos dados para a cidade escolhida
    df_lavra_mun = df_lavra[df_lavra['Municipio(s)'] == cidade_selecionada]
    df_alvara_mun = df_alvara[df_alvara['Municipio(s)'] == cidade_selecionada]
    

    # 3. Bloco de Informações da Cidade (O que abre ao escolher)
    col_1, col_2 = st.columns([1, 2])

    st.markdown(f"### ℹ️ {cidade_selecionada}")

    # Criando 3 colunas para as métricas principais
    col_1, col_2, col_3 = st.columns(3)

    with col_1:
        st.metric("🚚 Títulos de Lavra", len(df_lavra_mun))

    with col_2:
        st.metric("🔍 Títulos de Pesquisa", len(df_alvara_mun))

    with col_3:
        # Contagem de CPFs e CNPJs únicos na base de Lavra para a cidade
        # doc_limpo contém os documentos sem pontuação
        num_titulares_lavra = df_lavra_mun['doc_limpo'].nunique()
        st.metric("🏢 Empresas/CPFs Lavrando", num_titulares_lavra)



    # --- GRÁFICO 1 (PRINCIPAIS SUBSTâNCIAS LAVRADAS) ---
    st.markdown("### Substâncias Lavradas")
    if not df_lavra_mun.empty:
        # 1. Transformar a coluna em strings, separar por vírgula e transformar em lista
        subst_series = df_lavra_mun['Substância(s)'].str.split(',')
        
        # 2. "Explodir" a lista (cada item da lista vira uma linha) e limpar espaços extras
        subst_unificadas = subst_series.explode().str.strip().str.upper()
        
        # 3. Criar um DataFrame de contagem para o gráfico
        df_contagem_subst = subst_unificadas.value_counts().reset_index()
        df_contagem_subst.columns = ['Substância', 'Frequência']

        # 4. Gerar o gráfico com as substâncias isoladas
        fig_subst = px.pie(
            df_contagem_subst, 
            names='Substância', 
            values='Frequência',
            hole=0.4,
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        
        fig_subst.update_layout(showlegend=True)
        st.plotly_chart(fig_subst, use_container_width=True)
    else:
        st.info("Cidade focada atualmente em Pesquisa Mineral.")


    # --- GRÁFICO 2 (SUBSTÂNCIAS PESQUISADAS) ---

    def agrupar_minerais_raros(df_contagem, limite=0.03):
        """Agrupa substâncias abaixo do limite e retorna o DF final e o detalhamento dos raros."""
        total = df_contagem['Frequência'].sum()
        df_contagem['Porcentagem'] = (df_contagem['Frequência'] / total)
        
        acima = df_contagem[df_contagem['Porcentagem'] >= limite].copy()
        abaixo = df_contagem[df_contagem['Porcentagem'] < limite].copy()
        
        if not abaixo.empty:
            nova_linha = pd.DataFrame({
                'Substância': ['OUTRAS SUBSTÂNCIAS'],
                'Frequência': [abaixo['Frequência'].sum()],
                'Porcentagem': [abaixo['Porcentagem'].sum()]
            })
            df_final = pd.concat([acima, nova_linha], ignore_index=True)
            return df_final, abaixo.sort_values('Porcentagem', ascending=False)
        
        return acima, pd.DataFrame()

    # --- APLICAÇÃO NO GRÁFICO DE PESQUISA ---
    if not df_alvara_mun.empty:
        subst_pesq_unificadas = df_alvara_mun['Substância(s)'].str.split(',').explode().str.strip().str.upper()
        df_contagem_pesq = subst_pesq_unificadas.value_counts().reset_index()
        df_contagem_pesq.columns = ['Substância', 'Frequência']
        
        # Recebendo o DF agrupado e o DF de detalhes (abaixo de 3%)
        df_final_pesq, df_detalhes_outros = agrupar_minerais_raros(df_contagem_pesq, limite=0.03)

        fig_pesq = px.pie(
            df_final_pesq, 
            names='Substância', 
            values='Frequência',
            hole=0.4,
            title="Substâncias Pesquisadas",
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        
        st.plotly_chart(fig_pesq, use_container_width=True)

        # --- INTERAÇÃO PARA DETALHAMENTO ---
        if not df_detalhes_outros.empty:
            with st.popover("🔍 Ver detalhamento de 'Outras Substâncias'"):
                st.markdown("### Composição do grupo 'Outras'")
                st.write("Estes minerais representam individualmente menos de 3% do total:")
                
                # Formatação para exibição
                df_exibir = df_detalhes_outros[['Substância', 'Porcentagem']].copy()
                df_exibir['Porcentagem'] = (df_exibir['Porcentagem'] * 100).map('{:.2f}%'.format)
                
                st.table(df_exibir) # Lista simples e limpa



        # --- GRÁFICO 3 (PERFIL ESTRATÉGICO DOS TITULARES - LAVRA) ---
        def classificar_estrategico(row, df_l, df_p):
            titular = str(row['Titular']).strip()
            doc = str(row['doc_limpo']).strip()
            
            if len(doc) <= 11:
                return "Independentes/CPF"
            
            nome_upper = titular.upper()
            
            # Filtros de portfólio (usando o nome limpo)
            processos_lavra = df_l[df_l['Titular'] == titular]
            processos_pesq = df_p[df_p['Titular'] == titular]
            
            # 1. Estrelas do Lítio
            termos_litio = ["LITHIUM", "LITIO", "SIGMA", "CBL", "ATLAS", "LATIN RESOURCES"]
            if any(termo in nome_upper for termo in termos_litio):
                return "Estrelas do Lítio"
                
            # 2. Detentoras de Ativos (Baixamos para 5 para garantir que o contador suba)
            if len(processos_lavra) >= 5:
                return "Detentoras de Ativos"
                
            # 3. Prospectoras Juniores
            if len(processos_pesq) > 5 and len(processos_lavra) == 0:
                return "Prospectoras Juniores"
                
            return "Mineradores de Base"
    
        st.markdown("### Perfil Estratégico dos Titulares (Lavra)")


        if not df_lavra_mun.empty:
            # 1. Aplicar a nova classificação estratégica aos dados da cidade
            df_perfil = df_lavra_mun.copy()
            df_perfil['Categoria'] = df_perfil.apply(lambda x: classificar_estrategico(x, df_lavra, df_alvara), axis=1)

            # 2. Contagem por Categoria baseada em titulares únicos
            df_contagem_perfil = df_perfil.drop_duplicates(subset=['doc_limpo'])['Categoria'].value_counts().reset_index()
            df_contagem_perfil.columns = ['Categoria', 'Qtd']

            # 3. Gerar o gráfico de pizza com o novo mapa de cores
            fig_perfil = px.pie(
                df_contagem_perfil,
                names='Categoria',
                values='Qtd',
                hole=0.4,
                template="plotly_white",
                color='Categoria',
                color_discrete_map={
                    "Estrelas do Lítio": "#00CC96",
                    "Detentoras de Ativos": "#636EFA",
                    "Prospectoras Juniores": "#EF553B",
                    "Mineradores de Base": "#AB63FA",
                    "Independentes/CPF": "#FECB52"
                }
            )

            fig_perfil.update_layout(showlegend=True, legend=dict(orientation="h", y=-0.1))
            st.plotly_chart(fig_perfil, use_container_width=True)
        else:
            st.info("Dados insuficientes para classificar titulares nesta cidade.")

        # --- LISTA DETALHADA POR CATEGORIA ---
    if not df_lavra_mun.empty:
        st.markdown("---")
        st.markdown("### 🔍 Consultar Titulares por Perfil")
        
        # Criando o seletor baseado nos novos nomes das categorias
        opcoes_perfil = sorted(df_perfil['Categoria'].unique())
        categoria_para_ver = st.selectbox(
            "Escolha um perfil para listar as empresas/pessoas:",
            options=opcoes_perfil
        )

        # Filtrando os titulares únicos da categoria selecionada
        titulares_filtrados = df_perfil[df_perfil['Categoria'] == categoria_para_ver].drop_duplicates(subset=['doc_limpo'])

        if not titulares_filtrados.empty:
            st.write(f"Encontrados **{len(titulares_filtrados)}** titulares como '{categoria_para_ver}' em {cidade_selecionada}:")
            
            df_lista_exibir = titulares_filtrados[['Titular', 'doc_limpo']].copy()
            df_lista_exibir.columns = ['Nome do Titular', 'Documento']
            
            st.dataframe(df_lista_exibir, use_container_width=True, hide_index=True)
        else:
            st.info(f"Nenhum titular classificado como '{categoria_para_ver}' nesta cidade.")








# ==============================================================================
# ABA: PANORAMA POR SUBSTÂNCIA
# ==============================================================================
elif aba_selecionada == "Panorama por Substância":
    st.title("🪨 Panorama por Grupos de Substâncias")

    # --- 1. CONFIGURAÇÕES E MAPEAMENTOS ---
    grupos_minerarios = {
        'METAIS E BATERIAS': ['LÍTIO', 'MINÉRIO DE LÍTIO', 'ESPODUMÊNIO', 'PETALITA', 'AMBLIGONITA', 'OURO', 'MINÉRIO DE OURO', 'ESTANHO', 'CASSITERITA', 'TÂNTALO', 'TANTALITA', 'COLUMBITA'],
        'ROCHAS ORNAMENTAIS': ['GRANITO', 'QUARTZITO', 'MÁRMORE', 'XISTO', 'PEGMATITO', 'GRANODIORITO'],
        'MINERAIS INDUSTRIAIS': ['FELDSPATO', 'QUARTZO', 'CAULIM', 'MICA', 'ARGILA', 'GRAFITA', 'FOSFATO', 'BERILO', 'CASCALHO'],
        'GEMAS E PRECIOSAS': ['GEMA', 'TURMALINA', 'DIAMANTE', 'CASCALHO DIAMANTÍFERO', 'PEDRA CORADA', 'AQUAMARINA']
    }

    def identificar_grupo(substancia):
        substancia = str(substancia).upper()
        for grupo, lista in grupos_minerarios.items():
            if substancia in lista: return grupo
        return 'OUTROS'

    # --- 2. PROCESSAMENTO DE DADOS (FREQUÊNCIA GLOBAL) ---
    # Lavra
    subst_lavra_series = df_lavra['Substância(s)'].str.split(',').explode().str.strip().str.upper()
    df_freq_lavra = subst_lavra_series.value_counts().reset_index()
    df_freq_lavra.columns = ['Substância', 'Lavra']
    
    # Pesquisa
    subst_pesq_series = df_alvara['Substância(s)'].str.split(',').explode().str.strip().str.upper()
    df_freq_pesq = subst_pesq_series.value_counts().reset_index()
    df_freq_pesq.columns = ['Substância', 'Pesquisa']

    # Merge e Classificação por Grupo
    df_comp = pd.merge(df_freq_lavra, df_freq_pesq, on='Substância', how='outer').fillna(0)
    df_comp['Grupo'] = df_comp['Substância'].apply(identificar_grupo)

    # --- 3. FILTRO INDIVIDUAL (BUSCA DETALHADA) ---
    st.markdown("---")
    st.subheader("🔍 Busca Detalhada por Substância")
    
    lista_substancias = sorted(df_comp['Substância'].unique())
    substancia_selecionada = st.selectbox(
        "Selecione uma substância para análise profunda:",
        options=["Selecione..."] + lista_substancias
    )

    if substancia_selecionada != "Selecione...":
        # Métricas Rápidas
        dados_subst = df_comp[df_comp['Substância'] == substancia_selecionada]
        m1, m2 = st.columns(2)
        m1.metric(f"Títulos de Lavra", int(dados_subst['Lavra'].iloc[0]))
        m2.metric(f"Títulos de Pesquisa", int(dados_subst['Pesquisa'].iloc[0]))

        # Gráfico 1: Ocorrência Geográfica
        st.write(f"**Ocorrência de {substancia_selecionada} por Município**")
        loc_lavra = df_lavra[df_lavra['Substância(s)'].str.contains(substancia_selecionada, na=False, case=False)].copy()
        loc_pesq = df_alvara[df_alvara['Substância(s)'].str.contains(substancia_selecionada, na=False, case=False)].copy()
        
        c_lavra = loc_lavra.groupby('Municipio(s)').size().reset_index(name='Lavra')
        c_pesq = loc_pesq.groupby('Municipio(s)').size().reset_index(name='Pesquisa')
        df_geo_subst = pd.merge(c_lavra, c_pesq, on='Municipio(s)', how='outer').fillna(0)
        
        fig_geo = px.bar(df_geo_subst, x="Municipio(s)", y=["Lavra", "Pesquisa"], barmode="group",
                         color_discrete_map={"Pesquisa": "red", "Lavra": "green"}, template="plotly_white")
        st.plotly_chart(fig_geo, use_container_width=True)

        # Gráfico 2: Evolução Histórica (Linha com Marcadores e Zeros Preenchidos)
        st.write(f"**Evolução Histórica de Requerimentos**")
        loc_lavra['Ano'] = loc_lavra['Processo'].str.split('/').str[-1].astype(int)
        loc_pesq['Ano'] = loc_pesq['Processo'].str.split('/').str[-1].astype(int)
        
        t_pesq = loc_pesq.groupby('Ano').size().reset_index(name='Pesquisa')
        t_lavra = loc_lavra.groupby('Ano').size().reset_index(name='Lavra')
        df_t = pd.merge(t_pesq, t_lavra, on='Ano', how='outer').fillna(0)
        df_t = df_t[df_t['Ano'] >= 1930]

        if not df_t.empty:
            anos_full = pd.DataFrame({'Ano': range(int(df_t['Ano'].min()), int(df_t['Ano'].max()) + 1)})
            df_t_adj = pd.merge(anos_full, df_t, on='Ano', how='left').fillna(0)
            
            fig_hist = px.line(df_t_adj, x="Ano", y=["Pesquisa", "Lavra"], markers=True,
                               color_discrete_map={"Pesquisa": "red", "Lavra": "green"}, template="plotly_white")
            fig_hist.update_traces(line=dict(dash='dash'))
            fig_hist.update_layout(xaxis=dict(tickmode='linear', dtick=5), legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig_hist, use_container_width=True)

        # --- GRÁFICO 3: DETALHAMENTO DE TITULARES (LAVRA vs PESQUISA) ---
        st.write(f"**Principais Operadores e Pesquisadores**")
        col_l, col_p = st.columns(2)

        with col_l:
            titulares_l = loc_lavra.groupby('Titular').size().reset_index(name='Qtd').sort_values('Qtd', ascending=False).head(10)
            if not titulares_l.empty:
                st.caption("Top 10: Lavra")
                fig_pl = px.pie(
                    titulares_l, 
                    names="Titular", 
                    values="Qtd", 
                    hole=0.4, 
                    template="plotly_white",
                    height=500  # Aumenta a altura para o gráfico crescer
                )
                # Move a legenda para baixo para liberar espaço lateral para o gráfico
                fig_pl.update_layout(
                    legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5),
                    margin=dict(t=20, b=20, l=20, r=20)
                )
                st.plotly_chart(fig_pl, use_container_width=True)
            else: 
                st.info("Sem lavra ativa.")

        with col_p:
            titulares_p = loc_pesq.groupby('Titular').size().reset_index(name='Qtd').sort_values('Qtd', ascending=False).head(10)
            if not titulares_p.empty:
                st.caption("Top 10: Pesquisa")
                fig_pp = px.bar(
                    titulares_p, 
                    y="Titular", 
                    x="Qtd", 
                    orientation='h', 
                    color_discrete_sequence=['red'], 
                    template="plotly_white",
                    height=500  # Mantém a mesma altura para alinhar visualmente
                )
                fig_pp.update_layout(yaxis={'categoryorder':'total ascending'}, yaxis_title=None)
                st.plotly_chart(fig_pp, use_container_width=True)
            else: 
                st.info("Sem pesquisa ativa.")

    # --- 4. PANORAMA GERAL POR GRUPOS ---
    st.markdown("---")
    st.header("🪨 Panorama por Grupos de Substâncias")

    for grupo in grupos_minerarios.keys():
        df_grupo = df_comp[df_comp['Grupo'] == grupo]
        if not df_grupo.empty:
            with st.expander(f"📊 Grupo: {grupo}", expanded=True):
                fig_g = px.bar(df_grupo, x="Substância", y=["Lavra", "Pesquisa"], barmode="group",
                               color_discrete_map={"Pesquisa": "red", "Lavra": "green"}, 
                               template="plotly_white", height=350)
                fig_g.update_layout(margin=dict(l=20, r=20, t=10, b=10), legend=dict(orientation="h", y=1.1))
                st.plotly_chart(fig_g, use_container_width=True)

        




# ==============================================================================
# ABA: PANORAMA DAS EMPRESAS
# ==============================================================================
elif aba_selecionada == "Panorama das Empresas":
    st.title("🏢 Panorama Estratégico dos Titulares")

    # --- EXPLICAÇÃO DOS PERFIS (CABEÇALHO) ---
    with st.expander("ℹ️ Entenda a Classificação Estratégica"):
        st.markdown("""
        Para facilitar a análise de mercado, as empresas e titulares foram segmentados em cinco perfis estratégicos baseados em seu comportamento mineral e portfólio de direitos:
        
        *   **⭐ Estrelas do Lítio**: Players de alta relevância (Tier 1) com foco direto em minerais para baterias, detentores das plantas de beneficiamento e projetos globais.
        *   **🏛️ Detentoras de Ativos**: Empresas consolidadas que possuem um grande volume de títulos de lavra (5 ou mais), representando o patrimônio mineral estabelecido na região.
        *   **🚀 Prospectoras Juniores**: Empresas focadas em exploração mineral agressiva, com alto volume de autorizações de pesquisa, mas que ainda não iniciaram a fase de extração (lavra).
        *   **🏗️ Mineradores de Base**: O alicerce industrial do Vale, composto por mineradoras de médio e pequeno porte focadas em rochas ornamentais e minerais industriais.
        *   **👤 Independentes/CPF**: Profissionais liberais, pequenos proprietários e garimpeiros artesanais que detêm direitos minerais em nome próprio.
        """)

        
    # --- 1. CONFIGURAÇÕES E MAPEAMENTOS ---
    grupos_minerarios = {
        'METAIS E BATERIAS': ['LÍTIO', 'MINÉRIO DE LÍTIO', 'ESPODUMÊNIO', 'PETALITA', 'AMBLIGONITA', 'OURO', 'MINÉRIO DE OURO', 'ESTANHO', 'CASSITERITA', 'TÂNTALO', 'TANTALITA', 'COLUMBITA'],
        'ROCHAS ORNAMENTAIS': ['GRANITO', 'QUARTZITO', 'MÁRMORE', 'XISTO', 'PEGMATITO', 'GRANODIORITO'],
        'MINERAIS INDUSTRIAIS': ['FELDSPATO', 'QUARTZO', 'CAULIM', 'MICA', 'ARGILA', 'GRAFITA', 'FOSFATO', 'BERILO', 'CASCALHO'],
        'GEMAS E PRECIOSAS': ['GEMA', 'TURMALINA', 'DIAMANTE', 'CASCALHO DIAMANTÍFERO', 'PEDRA CORADA', 'AQUAMARINA']
    }

    def identificar_grupo(substancia):
        substancia = str(substancia).upper()
        for grupo, lista in grupos_minerarios.items():
            if substancia in lista: return grupo
        return 'OUTROS'

    # --- 2. CLASSIFICAÇÃO ESTRATÉGICA REFINADA ---
    def classificar_estrategico(row, df_l, df_p):
        titular = str(row['Titular']).strip()
        doc = str(row['doc_limpo']).strip()
        
        if len(doc) <= 11:
            return "Independentes/CPF"
        
        nome_upper = titular.upper()
        
        # Filtros de portfólio (usando o nome limpo)
        processos_lavra = df_l[df_l['Titular'] == titular]
        processos_pesq = df_p[df_p['Titular'] == titular]
        
        # 1. Estrelas do Lítio
        termos_litio = ["LITHIUM", "LITIO", "SIGMA", "CBL", "ATLAS", "LATIN RESOURCES"]
        if any(termo in nome_upper for termo in termos_litio):
            return "Estrelas do Lítio"
            
        # 2. Detentoras de Ativos (Baixamos para 5 para garantir que o contador suba)
        if len(processos_lavra) >= 5:
            return "Detentoras de Ativos"
            
        # 3. Prospectoras Juniores
        if len(processos_pesq) > 5 and len(processos_lavra) == 0:
            return "Prospectoras Juniores"
            
        return "Mineradores de Base"

    # --- PROCESSAMENTO SEGURO ---
    titulares_unicos = pd.concat([
        df_lavra[['Titular', 'doc_limpo']], 
        df_alvara[['Titular', 'doc_limpo']]
    ]).drop_duplicates('doc_limpo')

    # Forçar a limpeza dos nomes antes da classificação
    titulares_unicos['Titular'] = titulares_unicos['Titular'].astype(str).str.strip()
    df_lavra['Titular'] = df_lavra['Titular'].astype(str).str.strip()
    df_alvara['Titular'] = df_alvara['Titular'].astype(str).str.strip()

    titulares_unicos['Perfil'] = titulares_unicos.apply(lambda x: classificar_estrategico(x, df_lavra, df_alvara), axis=1)
    
    # Recalcula as métricas
    counts = titulares_unicos['Perfil'].value_counts()

    # --- 3. MÉTRICAS DE CABEÇALHO ---
    st.markdown("### 📊 Composição do Ecossistema Mineral")
    c1, c2, c3, c4, c5 = st.columns(5)
    
    c1.metric("⭐ Estrelas Lítio", counts.get("Estrelas do Lítio", 0))
    c2.metric("🏛️ Detentoras Ativos", counts.get("Detentoras de Ativos", 0))
    c3.metric("🚀 Juniores", counts.get("Prospectoras Juniores", 0))
    c4.metric("🏗️ Base/Indústria", counts.get("Mineradores de Base", 0))
    c5.metric("👤 CPFs", counts.get("Independentes/CPF", 0))
    st.divider()

    # --- 4. VISÃO GERAL (PIZZAS) ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎯 Perfil Estratégico (Titulares)")
        fig_perfil = px.pie(titulares_unicos, names='Perfil', hole=0.4,
                            color_discrete_map={
                                "Estrelas do Lítio": "#00CC96",
                                "Detentoras de Ativos": "#636EFA",
                                "Prospectoras Juniores": "#EF553B",
                                "Mineradores de Base": "#AB63FA",
                                "Independentes/CPF": "#FECB52"
                            }, template="plotly_white")
        fig_perfil.update_layout(legend=dict(orientation="h", y=-0.1))
        st.plotly_chart(fig_perfil, use_container_width=True)

    with col2:
        st.subheader("📦 Especialidade por Grupo")
        subst_geral = pd.concat([
            df_lavra['Substância(s)'].str.split(',').explode().str.strip().str.upper(),
            df_alvara['Substância(s)'].str.split(',').explode().str.strip().str.upper()
        ])
        df_grupos = subst_geral.apply(identificar_grupo).value_counts().reset_index()
        df_grupos.columns = ['Grupo', 'Qtd']
        fig_grupos = px.pie(df_grupos, names='Grupo', values='Qtd', hole=0.4,
                            color_discrete_sequence=px.colors.qualitative.Safe)
        fig_grupos.update_layout(legend=dict(orientation="h", y=-0.1))
        st.plotly_chart(fig_grupos, use_container_width=True)

    st.divider()

    # --- 5. RANKINGS DE DOMINÂNCIA ---
    st.subheader("🏆 Maiores Detentores de Direitos")
    col3, col4 = st.columns(2)

    with col3:
        st.write("**Top 10: Operadores (Lavra)**")
        rank_l = df_lavra['Titular'].value_counts().reset_index().head(10)
        rank_l.columns = ['Titular', 'Qtd']
        fig_l = px.bar(rank_l, y='Titular', x='Qtd', orientation='h', color_discrete_sequence=['green'], template="plotly_white")
        fig_l.update_layout(yaxis={'categoryorder':'total ascending'}, yaxis_title=None)
        st.plotly_chart(fig_l, use_container_width=True)

    with col4:
        st.write("**Top 10: Prospectores (Pesquisa)**")
        rank_p = df_alvara['Titular'].value_counts().reset_index().head(10)
        rank_p.columns = ['Titular', 'Qtd']
        fig_p = px.bar(rank_p, y='Titular', x='Qtd', orientation='h', color_discrete_sequence=['red'], template="plotly_white")
        fig_p.update_layout(yaxis={'categoryorder':'total ascending'}, yaxis_title=None)
        st.plotly_chart(fig_p, use_container_width=True)

    # --- 6. INVESTIGAÇÃO INDIVIDUAL (MENU SUSPENSO) ---
    st.markdown("---")
    st.subheader("🔍 Investigação por Titular")

    lista_titulares = sorted([str(t) for t in titulares_unicos['Titular'].dropna().unique()])
    titular_selecionado = st.selectbox(
        "Selecione uma empresa ou CPF para detalhamento estratégico:",
        options=["Selecione..."] + lista_titulares
    )

    if titular_selecionado != "Selecione...":
        t_lavra = df_lavra[df_lavra['Titular'] == titular_selecionado].copy()
        t_pesq = df_alvara[df_alvara['Titular'] == titular_selecionado].copy()
        
        # Tenta buscar o perfil; se não achar, reclassifica na hora
        try:
            perfil_t = titulares_unicos[titulares_unicos['Titular'] == titular_selecionado]['Perfil'].iloc[0]
        except:
            perfil_t = "N/A"
            
        st.info(f"**Perfil Estratégico:** {perfil_t}")
        
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("Processos em Lavra", len(t_lavra))
        m_col2.metric("Processos em Pesquisa", len(t_pesq))
        
        cidades_unicas = pd.concat([t_lavra['Municipio(s)'], t_pesq['Municipio(s)']]).nunique()
        m_col3.metric("Cidades de Atuação", cidades_unicas)

        col_detalhe1, col_detalhe2 = st.columns(2)

        with col_detalhe1:
            st.write(f"**Capilaridade Geográfica**")
            geo_l = t_lavra.groupby('Municipio(s)').size().reset_index(name='Lavra')
            geo_p = t_pesq.groupby('Municipio(s)').size().reset_index(name='Pesquisa')
            df_geo_t = pd.merge(geo_l, geo_p, on='Municipio(s)', how='outer').fillna(0)
            
            fig_geo_t = px.bar(
                df_geo_t, x="Municipio(s)", y=["Lavra", "Pesquisa"],
                barmode="group", color_discrete_map={"Pesquisa": "red", "Lavra": "green"},
                template="plotly_white"
            )
            fig_geo_t.update_layout(xaxis_title=None, yaxis_title="Nº Títulos", legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig_geo_t, use_container_width=True)

        with col_detalhe2:
            st.write(f"**Mix de Substâncias**")
            subst_t = pd.concat([
                t_lavra['Substância(s)'].str.split(',').explode().str.strip().str.upper(),
                t_pesq['Substância(s)'].str.split(',').explode().str.strip().str.upper()
            ]).value_counts().reset_index()
            subst_t.columns = ['Substância', 'Qtd']
            
            if not subst_t.empty:
                fig_subst_t = px.pie(
                    subst_t, names='Substância', values='Qtd', 
                    hole=0.4, template="plotly_white",
                    color_discrete_sequence=px.colors.qualitative.Prism
                )
                fig_subst_t.update_layout(legend=dict(orientation="h", y=-0.2))
                st.plotly_chart(fig_subst_t, use_container_width=True)
            else:
                st.warning("Não há dados de substâncias vinculados.")

        with st.expander(f"📄 Listagem Técnica de Processos - {titular_selecionado}"):
            df_lista = pd.concat([
                t_lavra[['Processo', 'Fase Atual', 'Municipio(s)', 'Substância(s)']],
                t_pesq[['Processo', 'Fase Atual', 'Municipio(s)', 'Substância(s)']]
            ])
            st.dataframe(df_lista, use_container_width=True)
