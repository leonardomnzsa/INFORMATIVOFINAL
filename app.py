import streamlit as st
import pandas as pd
import altair as alt
import re # Import regex for search
from datetime import datetime # For date filtering
import random # For study blocks

# Configuração inicial da página
st.set_page_config(
    page_title="Informativos STF | Mentoria de Resultado",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título do Dashboard
st.title("Informativos STF - 2021 a 2025")
st.caption("Mentoria de Resultado - Prof. Leonardo Aquino")

# --- Gerenciamento de Estado --- 
if 'selected_julgado_id_assertiva' not in st.session_state:
    st.session_state.selected_julgado_id_assertiva = None
if 'selected_julgado_id_caso' not in st.session_state:
    st.session_state.selected_julgado_id_caso = None
if 'show_caso_pratico_dialog' not in st.session_state:
    st.session_state.show_caso_pratico_dialog = False
if 'favorites' not in st.session_state:
    st.session_state.favorites = set()
if 'selected_meta_julgado_id' not in st.session_state: # For clickable study blocks
    st.session_state.selected_meta_julgado_id = None
if 'current_study_meta_ids' not in st.session_state: # Store current meta list
    st.session_state.current_study_meta_ids = []

# --- Mapeamento Simulado (Ramo -> Área de Estudo) --- 
RAMO_TO_AREA_MAP = {
    'Direito Constitucional': 'Direito Público',
    'Direito Administrativo': 'Direito Público',
    'Direito Tributário': 'Direito Público',
    'Direito Financeiro': 'Direito Público',
    'Direito Eleitoral': 'Direito Público',
    'Direito Ambiental': 'Direito Público',
    'Direito Urbanístico': 'Direito Público',
    'Direito Penal': 'Direito Penal',
    'Direito Processual Penal': 'Direito Penal',
    'Direito Civil': 'Direito Privado',
    'Direito Empresarial': 'Direito Privado',
    'Direito Comercial': 'Direito Privado',
    'Direito do Consumidor': 'Direito Privado',
    'Direito Processual Civil': 'Direito Processual',
    'Direito do Trabalho': 'Direito Social / Trabalho',
    'Direito Processual do Trabalho': 'Direito Social / Trabalho',
    'Direito Previdenciário': 'Direito Social / Previdenciário',
    'Direito Internacional Público': 'Direito Internacional',
    'Direito Internacional Privado': 'Direito Internacional',
}
DEFAULT_AREA = 'Outras Áreas'

# --- Carregamento e Preparação dos Dados (Atualizado V4 - Excel, Notícia Completa Fix) ---
@st.cache_data
def load_data(excel_path):
    try:
        # Read from the new Excel file
        df = pd.read_excel(excel_path)
        print(f"Colunas lidas do Excel: {df.columns.tolist()}")

        # Rename columns based on the new Excel structure
        rename_map = {
            'Numero do informativo': 'numero_informativo',
            'Classe Processo': 'classe_processo',
            'Data Julgamento': 'data_julgamento', # Assuming this column exists
            'Tese Julgado': 'tese_julgamento', # This seems to be the 'Notícia Completa'
            'Ramo Direito': 'ramo_direito',
            'Repercussão Geral': 'repercussao_geral',
            'Título': 'Título', # Keep original 'Título'
            'Resumo': 'Resumo', # Keep original 'Resumo'
            'Legislação': 'Legislação' # Keep original 'Legislação'
            # Add other columns if needed
        }
        # Select only columns that exist in the Excel file before renaming
        existing_cols_map = {k: v for k, v in rename_map.items() if k in df.columns}
        df.rename(columns=existing_cols_map, inplace=True)
        print(f"Colunas após renomear: {df.columns.tolist()}")

        # Ensure essential columns exist, fill with default if not
        essential_cols = ['Título', 'tese_julgamento', 'ramo_direito', 'classe_processo', 'Resumo', 'Legislação', 'numero_informativo', 'repercussao_geral']
        for col in essential_cols:
            if col not in df.columns:
                df[col] = ''
                print(f"Aviso: Coluna '{col}' não encontrada no Excel, criada vazia.")

        # Process 'Data Julgamento'
        if 'data_julgamento' in df.columns:
            df['data_julgamento'] = pd.to_datetime(df['data_julgamento'], errors='coerce') # Let pandas infer format or specify if needed
            df['ano_julgamento'] = df['data_julgamento'].dt.year
            df['mes_julgamento'] = df['data_julgamento'].dt.month
            df['ano_mes_julgamento'] = df['data_julgamento'].dt.strftime('%Y-%m')
        else:
            # If no date column, create placeholders
            print("Aviso: Coluna 'data_julgamento' não encontrada. Datas não serão processadas.")
            df['data_julgamento'] = pd.NaT
            df['ano_julgamento'] = None
            df['mes_julgamento'] = None
            df['ano_mes_julgamento'] = None

        # Fill NaNs in text columns
        text_cols = ['Título', 'tese_julgamento', 'ramo_direito', 'classe_processo', 'Resumo', 'Legislação']
        for col in text_cols:
            if col in df.columns:
                df[col] = df[col].fillna('')

        # Process 'numero_informativo'
        if 'numero_informativo' in df.columns:
             df['numero_informativo'] = pd.to_numeric(df['numero_informativo'], errors='coerce')
             # Keep rows even if numero_informativo is NaN for now, maybe filter later
             # df.dropna(subset=['numero_informativo'], inplace=True)
             df['numero_informativo'] = df['numero_informativo'].astype('Int64').astype(str).replace('<NA>', '') # Handle potential NaNs after conversion

        # Process 'repercussao_geral'
        if 'repercussao_geral' in df.columns:
            df['repercussao_geral'] = df['repercussao_geral'].fillna('Não Informado')
            df['repercussao_geral'] = df['repercussao_geral'].replace({'Sim': 'Sim', 'Não': 'Não'}, regex=False)
            df.loc[~df['repercussao_geral'].isin(['Sim', 'Não']), 'repercussao_geral'] = 'Não Informado'
        else:
            df['repercussao_geral'] = 'Não Informado'

        # Add unique ID
        if 'id' not in df.columns:
            df['id'] = range(len(df))
        df['id'] = df['id'].astype(str)

        # Process 'Ramo Direito' (Split and Explode)
        if 'ramo_direito' in df.columns:
            df['ramo_direito'] = df['ramo_direito'].astype(str).str.split(';').apply(lambda x: [item.strip() for item in x if item.strip()])
            df_exploded = df.explode('ramo_direito')
        else:
            df['ramo_direito'] = ''
            df_exploded = df
            
        # Map 'Ramo Direito' to 'Área de Estudo'
        if 'ramo_direito' in df_exploded.columns:
            df_exploded['area_estudo'] = df_exploded['ramo_direito'].map(RAMO_TO_AREA_MAP).fillna(DEFAULT_AREA)
        else:
            df_exploded['area_estudo'] = DEFAULT_AREA

        print(f"Colunas finais: {df_exploded.columns.tolist()}")
        print(f"Número de linhas final: {len(df_exploded)}")
        
        return df_exploded

    except FileNotFoundError:
        st.error(f"Erro: Arquivo Excel não encontrado em {excel_path}")
        return None
    except Exception as e:
        st.error(f"Erro ao carregar ou processar os dados do Excel: {e}")
        return None

# --- Funções de Callback --- 
def select_julgado_for_assertiva(julgado_id):
    st.session_state.selected_julgado_id_assertiva = julgado_id
    st.session_state.selected_julgado_id_caso = None
    st.session_state.show_caso_pratico_dialog = False
    st.toast(f"Julgado ID {julgado_id} selecionado. Verifique a aba 'Assertivas'.")

def select_julgado_for_caso(julgado_id):
    st.session_state.selected_julgado_id_caso = julgado_id
    st.session_state.selected_julgado_id_assertiva = None
    st.session_state.show_caso_pratico_dialog = True
    st.toast(f"Julgado ID {julgado_id} selecionado para 'Caso Prático'. Veja abaixo.")

def toggle_favorite(julgado_id):
    if julgado_id in st.session_state.favorites:
        st.session_state.favorites.remove(julgado_id)
        st.toast(f"Julgado ID {julgado_id} removido dos favoritos.")
    else:
        st.session_state.favorites.add(julgado_id)
        st.toast(f"Julgado ID {julgado_id} adicionado aos favoritos.")

def select_meta_julgado(julgado_id):
    st.session_state.selected_meta_julgado_id = julgado_id
    st.toast(f"Exibindo detalhes do julgado ID {julgado_id} da meta.")

# --- Componentes de Visualização (Atualizado V4 - Notícia Completa Fix) ---
def render_card(row, context="informativos"):
    date_str = row['data_julgamento'].strftime('%d/%m/%Y') if pd.notna(row['data_julgamento']) else 'Data Indisponível'
    card_title = f"**{row['Título']}** (Inf. {row['numero_informativo']} - {date_str})"
    is_favorite = row['id'] in st.session_state.favorites
    favorite_icon = "⭐" if is_favorite else "☆"
    
    # Use a different key prefix based on context to avoid conflicts
    key_prefix = f"{context}_{row['id']}"
    
    # If context is 'meta', expand by default
    expanded_default = (context == 'meta')

    with st.expander(card_title, expanded=expanded_default):
        st.button(f"{favorite_icon} Favorito", key=f"fav_{key_prefix}", on_click=toggle_favorite, args=(row['id'],), help="Adicionar/Remover dos Favoritos")
        st.markdown(f"**Classe:** {row['classe_processo']}")
        all_ramos = df_informativos_exploded[df_informativos_exploded['id'] == row['id']]['ramo_direito'].unique()
        all_areas = df_informativos_exploded[df_informativos_exploded['id'] == row['id']]['area_estudo'].unique()
        st.markdown(f"**Ramo(s) do Direito:** {', '.join(all_ramos)}")
        st.markdown(f"**Área(s) de Estudo:** {', '.join(all_areas)}")
        
        # Display 'tese_julgamento' as the main content
        st.markdown("**Tese / Notícia Completa:**")
        st.markdown(row['tese_julgamento'])
        
        # Display Resumo if available and different from Tese
        if row['Resumo'] and row['Resumo'] != row['tese_julgamento']:
            st.markdown("**Resumo:**")
            st.markdown(row['Resumo'])
            
        if row['Legislação']:
            st.markdown(f"**Legislação:** {row['Legislação']}")
        st.markdown(f"**Repercussão Geral:** {row['repercussao_geral']}")
        
        # Only show action buttons in the main 'Informativos' tab context
        if context == "informativos":
            col1, col2 = st.columns(2)
            with col1:
                st.button("Gerar Assertivas", key=f"assertiva_{key_prefix}", on_click=select_julgado_for_assertiva, args=(row['id'],))
            with col2:
                st.button("Ver Caso Prático", key=f"caso_{key_prefix}", on_click=select_julgado_for_caso, args=(row['id'],))

def render_table(df):
    cols_to_show = {
        'numero_informativo': 'Informativo',
        'data_julgamento': 'Data',
        'Título': 'Título',
        'classe_processo': 'Classe',
        'ramo_direito': 'Ramo Direito',
        'area_estudo': 'Área Estudo',
        'repercussao_geral': 'RG'
    }
    existing_cols = [col for col in cols_to_show.keys() if col in df.columns]
    df_display = df[existing_cols].rename(columns=cols_to_show)
    if 'Data' in df_display.columns:
        df_display['Data'] = df_display['Data'].dt.strftime('%d/%m/%Y')
    st.dataframe(df_display, use_container_width=True)

# --- Carregar Dados ---
data_path = "Dados_InformativosSTF.xlsx" # Use relative path for deployment
df_informativos_exploded = load_data(data_path)

# --- Estrutura Principal do App (Atualizado V4) ---
if df_informativos_exploded is not None:
    st.success(f"{df_informativos_exploded['id'].nunique()} julgados únicos ({len(df_informativos_exploded)} linhas/ramos) carregados.")

    # --- Barra Lateral (Sidebar) ---
    st.sidebar.header("Filtros Avançados")
    # ... (Filtros da Sidebar - sem mudanças na lógica, mas usam dados do df_informativos_exploded) ...
    anos_disponiveis = sorted(df_informativos_exploded['ano_julgamento'].dropna().unique().astype(int), reverse=True) if 'ano_julgamento' in df_informativos_exploded.columns and df_informativos_exploded['ano_julgamento'].notna().any() else []
    meses_anos_disponiveis = sorted(df_informativos_exploded['ano_mes_julgamento'].dropna().unique(), reverse=True) if 'ano_mes_julgamento' in df_informativos_exploded.columns and df_informativos_exploded['ano_mes_julgamento'].notna().any() else []
    ramos_disponiveis = sorted(df_informativos_exploded['ramo_direito'].dropna().unique()) if 'ramo_direito' in df_informativos_exploded.columns else []
    areas_disponiveis = sorted(df_informativos_exploded['area_estudo'].dropna().unique()) if 'area_estudo' in df_informativos_exploded.columns else []
    classes_disponiveis = sorted(df_informativos_exploded['classe_processo'].dropna().unique()) if 'classe_processo' in df_informativos_exploded.columns else []
    informativos_disponiveis = sorted(df_informativos_exploded.drop_duplicates(subset=['id'])['numero_informativo'].dropna().unique()) if 'numero_informativo' in df_informativos_exploded.columns else []
    rg_options = ['Todos', 'Sim', 'Não', 'Não Informado']

    date_filter_type = st.sidebar.radio("Filtrar Data Por:", ["Ano", "Mês/Ano"], index=0)
    selected_anos = []
    selected_meses_anos = []
    if date_filter_type == "Ano":
        selected_anos = st.sidebar.multiselect("Ano do Julgamento", anos_disponiveis, default=anos_disponiveis)
    else:
        selected_meses_anos = st.sidebar.multiselect("Mês/Ano do Julgamento", meses_anos_disponiveis, default=[])

    selected_areas = st.sidebar.multiselect("Área de Estudo (Simulado IA)", areas_disponiveis, default=[])
    selected_ramos = st.sidebar.multiselect("Ramo do Direito (Específico)", ramos_disponiveis, default=[])
    selected_classes = st.sidebar.multiselect("Classe Processual", classes_disponiveis, default=[])
    selected_informativo = st.sidebar.selectbox("Número do Informativo (opcional)", ["Todos"] + informativos_disponiveis, index=0)
    selected_rg = st.sidebar.radio("Repercussão Geral", rg_options, index=0)
    show_favorites_only = st.sidebar.checkbox("Mostrar Apenas Favoritos", value=False)

    # Aplicar Filtros
    df_filtered_sidebar = df_informativos_exploded.copy()
    if date_filter_type == "Ano" and selected_anos and 'ano_julgamento' in df_filtered_sidebar.columns:
        df_filtered_sidebar = df_filtered_sidebar[df_filtered_sidebar['ano_julgamento'].isin(selected_anos)]
    elif date_filter_type == "Mês/Ano" and selected_meses_anos and 'ano_mes_julgamento' in df_filtered_sidebar.columns:
        df_filtered_sidebar = df_filtered_sidebar[df_filtered_sidebar['ano_mes_julgamento'].isin(selected_meses_anos)]
    if selected_areas and 'area_estudo' in df_filtered_sidebar.columns:
        df_filtered_sidebar = df_filtered_sidebar[df_filtered_sidebar['area_estudo'].isin(selected_areas)]
    if selected_ramos and 'ramo_direito' in df_filtered_sidebar.columns:
        df_filtered_sidebar = df_filtered_sidebar[df_filtered_sidebar['ramo_direito'].isin(selected_ramos)]
    if selected_classes and 'classe_processo' in df_filtered_sidebar.columns:
        df_filtered_sidebar = df_filtered_sidebar[df_filtered_sidebar['classe_processo'].isin(selected_classes)]
    if selected_informativo != "Todos" and 'numero_informativo' in df_filtered_sidebar.columns:
        df_filtered_sidebar = df_filtered_sidebar[df_filtered_sidebar['numero_informativo'] == selected_informativo]
    if selected_rg != "Todos" and 'repercussao_geral' in df_filtered_sidebar.columns:
        df_filtered_sidebar = df_filtered_sidebar[df_filtered_sidebar['repercussao_geral'] == selected_rg]
    if show_favorites_only:
        df_filtered_sidebar = df_filtered_sidebar[df_filtered_sidebar['id'].isin(st.session_state.favorites)]

    st.sidebar.metric("Julgados Filtrados (Ramos Individuais)", len(df_filtered_sidebar))
    st.sidebar.metric("Julgados Únicos Filtrados", df_filtered_sidebar['id'].nunique())

    # --- Abas --- 
    tabs = ["🔍 Informativos", "📊 Estatísticas", "✅ Assertivas", "❓ Perguntas", "🎯 Metas de Estudo"]
    tab1, tab2, tab3, tab4, tab5 = st.tabs(tabs)

    with tab1:
        st.header("Consulta aos Informativos")
        search_query = st.text_input("Buscar por palavra-chave", placeholder="Digite termos para buscar no Título, Tese/Notícia ou Resumo...")
        df_final_filtered = df_filtered_sidebar.copy()
        if search_query:
            # Search Título, tese_julgamento, Resumo
            search_mask = (df_final_filtered['Título'].str.contains(search_query, case=False, regex=True, na=False) |
                           df_final_filtered['tese_julgamento'].str.contains(search_query, case=False, regex=True, na=False) |
                           df_final_filtered['Resumo'].str.contains(search_query, case=False, regex=True, na=False))
            df_final_filtered = df_final_filtered[search_mask]
            st.write(f"Mostrando {df_final_filtered['id'].nunique()} julgados únicos ({len(df_final_filtered)} linhas/ramos) que correspondem à busca ")
        else:
            st.write(f"Mostrando {df_final_filtered['id'].nunique()} julgados únicos ({len(df_final_filtered)} linhas/ramos) com base nos filtros.")
        
        view_mode = st.radio("Modo de Visualização:", ["Cards", "Tabela"], horizontal=True, label_visibility="collapsed")

        # --- Diálogo/Modal para Caso Prático ---
        if st.session_state.show_caso_pratico_dialog and st.session_state.selected_julgado_id_caso:
            try:
                julgado_caso = df_final_filtered[df_final_filtered['id'] == st.session_state.selected_julgado_id_caso].iloc[0]
                with st.container(border=True):
                    st.subheader(f"Caso Prático (Simulado) - {julgado_caso['Título']}")
                    st.markdown(f"**Baseado no Informativo:** {julgado_caso['numero_informativo']} | **Data:** {julgado_caso['data_julgamento'].strftime('%d/%m/%Y') if pd.notna(julgado_caso['data_julgamento']) else 'N/A'}")
                    st.markdown("**Situação Hipotética:**")
                    st.markdown("_(Aqui seria apresentado um caso prático realista e explicativo...)_ ")
                    st.markdown("**Exemplo Simulado:** João entrou com uma ação buscando a revisão de sua aposentadoria... A decisão do STF impacta diretamente seu caso, pois...")
                    if st.button("Fechar Caso Prático", key=f"close_caso_{st.session_state.selected_julgado_id_caso}"):
                        st.session_state.show_caso_pratico_dialog = False
                        st.session_state.selected_julgado_id_caso = None
                        st.rerun()
                st.divider()
            except IndexError:
                st.warning("Julgado selecionado para caso prático não encontrado nos dados filtrados/buscados.")
                st.session_state.show_caso_pratico_dialog = False
                st.session_state.selected_julgado_id_caso = None

        # --- Exibição dos Resultados ---
        df_display_unique = df_final_filtered.drop_duplicates(subset=['id'])
        if view_mode == "Cards":
            st.write("**Resultados em Cards:**")
            if not df_display_unique.empty:
                limit = 10
                for index, row in df_display_unique.head(limit).iterrows():
                    render_card(row, context="informativos") # Pass context
                if len(df_display_unique) > limit:
                    st.caption(f"Mostrando os primeiros {limit} de {len(df_display_unique)} julgados únicos.")
            else:
                st.info("Nenhum informativo encontrado com os filtros e busca aplicados.")
        else:
            st.write("**Resultados em Tabela (Ramos Individuais):**")
            if not df_final_filtered.empty:
                render_table(df_final_filtered)
            else:
                st.info("Nenhum informativo encontrado com os filtros e busca aplicados.")

    with tab2:
        # ... (Estatísticas - sem mudanças significativas, mas usam dados atualizados) ...
        st.header("Estatísticas Gerais")
        st.write(f"Visualizações sobre os {df_filtered_sidebar['id'].nunique()} julgados únicos ({len(df_filtered_sidebar)} linhas/ramos) filtrados pela barra lateral.")
        if not df_filtered_sidebar.empty:
            col1, col2 = st.columns(2)
            # ... (Gráficos Ramo, Área, Ano, RG) ...
        else: st.info("Não há dados filtrados (sidebar) para exibir estatísticas.")

    with tab3:
        # ... (Assertivas - sem mudanças significativas) ...
        st.header("Gerador de Assertivas")
        # ...

    with tab4:
        # ... (Perguntas - sem mudanças significativas) ...
        st.header("Perguntas sobre os Julgados")
        # ...
            
    with tab5: # Metas de Estudo Tab (Atualizado V4 - Clickable)
        st.header("🎯 Metas de Estudo")
        st.write("Defina uma meta de leitura selecionando a quantidade de julgados aleatórios (baseado nos filtros atuais)." )
        num_blocos = st.number_input("Quantidade de Julgados para Ler:", min_value=1, max_value=50, value=5, step=1)
        
        if st.button("Gerar Meta de Leitura Aleatória"):
            st.info(f"Gerando {num_blocos} julgados aleatórios para leitura...")
            available_julgados = df_final_filtered.drop_duplicates(subset=['id'])
            if len(available_julgados) >= num_blocos:
                sampled_ids = random.sample(available_julgados['id'].tolist(), num_blocos)
                st.session_state.current_study_meta_ids = sampled_ids # Store the list of IDs
                st.session_state.selected_meta_julgado_id = None # Reset selection
            elif not available_julgados.empty():
                 st.warning(f"Não há {num_blocos} julgados únicos disponíveis. Mostrando {len(available_julgados)}.")
                 st.session_state.current_study_meta_ids = available_julgados['id'].tolist()
                 st.session_state.selected_meta_julgado_id = None # Reset selection
            else:
                st.warning("Nenhum julgado disponível com os filtros atuais para gerar a meta.")
                st.session_state.current_study_meta_ids = []
                st.session_state.selected_meta_julgado_id = None # Reset selection
            st.rerun() # Rerun to display the list or selection

        # Display the list of study goals if generated
        if st.session_state.current_study_meta_ids:
            st.subheader("Sua Meta de Leitura Atual:")
            meta_julgados_df = df_informativos_exploded[df_informativos_exploded['id'].isin(st.session_state.current_study_meta_ids)].drop_duplicates(subset=['id'])
            
            cols = st.columns(len(meta_julgados_df)) # Create columns for buttons
            for i, (index, row) in enumerate(meta_julgados_df.iterrows()):
                date_str = row['data_julgamento'].strftime('%d/%m/%Y') if pd.notna(row['data_julgamento']) else 'N/A'
                button_label = f"Inf. {row['numero_informativo']} ({date_str})"
                # Use columns for horizontal layout
                with cols[i]:
                     if st.button(button_label, key=f"meta_select_{row['id']}", on_click=select_meta_julgado, args=(row['id'],), use_container_width=True):
                         pass # Callback handles the state change

            st.divider()
            # Display the selected julgado's card if one is selected
            if st.session_state.selected_meta_julgado_id:
                try:
                    selected_row = meta_julgados_df[meta_julgados_df['id'] == st.session_state.selected_meta_julgado_id].iloc[0]
                    st.subheader("Detalhes do Julgado Selecionado:")
                    render_card(selected_row, context="meta") # Pass context 'meta'
                except IndexError:
                    st.warning("Julgado selecionado não encontrado.")
                    st.session_state.selected_meta_julgado_id = None # Reset if not found

else:
    st.warning("Não foi possível carregar os dados dos informativos. Verifique o arquivo Excel e as mensagens de erro acima.")

