# app.py
import streamlit as st
import traceback #

# Importações dos seus módulos de página da nova estrutura
from ui import dcm_page
from ui import coordenacao_page
from config import configs

# --- Configuração da Página e Título Principal ---
st.set_page_config(layout="wide", page_title="Sistema de Propostas") #

# --- Inicialização do Estado ---
if 'current_page' not in st.session_state: #
    st.session_state.current_page = "Gerador de Propostas" #
if 'generator_type' not in st.session_state: #
    st.session_state.generator_type = "DCM" #

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

cols_nav = st.columns(len(configs.PAGES))
for i, page_name in enumerate(configs.PAGES):
    if cols_nav[i].button(page_name, key=f"nav_btn_{page_name}"):
        st.session_state.current_page = page_name
        st.rerun()

st.markdown("---")

# --- Conteúdo da Página Selecionada ---

if st.session_state.current_page == "Gerador de Propostas": #
    st.title("Gerador de Propostas") #

    def update_generator_type(): #
        st.session_state.generator_type = st.session_state.generator_type_selector #

    current_generator_index = configs.GENERATOR_OPTIONS.index(st.session_state.generator_type) #

    st.radio( #
        "Selecione o tipo de gerador:",
        options=configs.GENERATOR_OPTIONS,
        index=current_generator_index, 
        horizontal=True, 
        key="generator_type_selector",
        on_change=update_generator_type 
    )
    
    st.markdown("---") #

    if st.session_state.generator_type == "DCM": #
        dcm_page.render_dcm_page() # Chamando a função da página DCM importada
    elif st.session_state.generator_type == "Coordenação": #
        coordenacao_page.render_coordenacao_page() # Chamando a função da página Coordenação importada

elif st.session_state.current_page == "Gerador de Recibos": #
    st.title("Gerador de Recibos") #
    st.write("Esta página ainda está em desenvolvimento.") #