import streamlit as st
import traceback

# Importações dos seus módulos de página e utilitários
from modules.pages import dcm_generator_page
from modules.pages import coordenacao_generator_page

# --- Configuração da Página e Título Principal ---
st.set_page_config(layout="wide", page_title="Sistema de Propostas")

# --- Inicialização do Estado ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Gerador de Propostas"
if 'generator_type' not in st.session_state:
    st.session_state.generator_type = "DCM"

# Nomes das páginas para a barra de navegação
PAGES = ["Gerador de Propostas", "Gerador de Recibos"]

# Criação da barra de navegação superior
st.markdown("""
<style>
    /* Seu CSS para botões de navegação e abas aqui */
    .stButton>button {
        width: 100%;
        border-radius: 0.5rem;
        border: 1px solid #CCCCCC;
        background-color: #FFFFFF;
        color: #212121 !important;
    }
    .stButton>button:hover {
        background-color: #F0F0F0;
        border-color: #B0B0B0;
        color: #000000 !important;
    }
    /* ... (restante do seu CSS) ... */
</style>
""", unsafe_allow_html=True)

cols_nav = st.columns(len(PAGES))
for i, page_name in enumerate(PAGES):
    if cols_nav[i].button(page_name, key=f"nav_btn_{page_name}"):
        st.session_state.current_page = page_name
        # if page_name != "Gerador de Propostas": # Não é mais necessário resetar aqui
        #     st.session_state.generator_type = "DCM"
        st.rerun() # Adicionar st.rerun() aqui pode ajudar na navegação principal

st.markdown("---")

# --- Conteúdo da Página Selecionada ---

if st.session_state.current_page == "Gerador de Propostas":
    st.title("Gerador de Propostas")

    generator_options = ["DCM", "Coordenação"]

    # Função de callback para o radio button
    def update_generator_type():
        # O valor do widget já estará em st.session_state.generator_type_selector
        # Apenas garantimos que st.session_state.generator_type também seja atualizado,
        # embora a atribuição direta após o st.radio já fizesse isso.
        # A principal utilidade do on_change aqui é forçar o Streamlit a
        # reconhecer uma mudança significativa que requer re-renderização.
        st.session_state.generator_type = st.session_state.generator_type_selector
        # Não é estritamente necessário st.rerun() aqui, pois a mudança de widget já o causa.

    current_generator_index = generator_options.index(st.session_state.generator_type)

    st.radio(
        "Selecione o tipo de gerador:",
        options=generator_options,
        index=current_generator_index,
        horizontal=True,
        key="generator_type_selector", # Usaremos esta chave no callback
        on_change=update_generator_type # Adiciona a função de callback
    )
    # A atribuição direta é redundante se on_change está atualizando st.session_state.generator_type
    # st.session_state.generator_type = st.radio(...)
    # No entanto, o st.radio em si não retorna o valor diretamente para ser atribuído
    # desta forma se on_change for usado para atualizar o estado principal.
    # O valor selecionado estará em st.session_state.generator_type_selector (a chave do widget)

    st.markdown("---")

    if st.session_state.generator_type == "DCM":
        dcm_generator_page.render_dcm_page()
    elif st.session_state.generator_type == "Coordenação":
        coordenacao_generator_page.render_coordenacao_page()

elif st.session_state.current_page == "Gerador de Recibos":
    st.title("Gerador de Recibos")
    st.write("Esta página ainda está em desenvolvimento.")