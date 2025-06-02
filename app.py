import streamlit as st
from io import BytesIO
import traceback

# Importações dos seus módulos customizados
from scripts.api import consultar_cnpj
from scripts.core_logic import (
    OFFER_TYPES_DETAILS, 
    OFFER_TYPE_OPTIONS, 
    format_cep,
    prepare_document_data
)
from scripts.doc_utils import generate_docx

# --- Configuração da Página e Título Principal ---
st.set_page_config(layout="wide", page_title="Sistema de Propostas")
# Não vamos usar st.title() globalmente, cada "página" pode ter o seu

# --- Definição das Páginas e Navegação ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Gerador de Propostas" # Página inicial

# Nomes das páginas para a barra de navegação
PAGES = ["Gerador de Propostas", "Dashboard", "Configurações", "Ajuda"]

# Criação da barra de navegação superior
st.markdown("""
<style>
    /* Seus estilos para .stButton>button que ajustamos antes */
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

    /* --- ESTILOS PARA AS ABAS (st.tabs) --- */
    div.stTabs[data-baseweb="tabs"] { 
        /* Estilo para o contêiner principal das abas, se necessário */
        /* border-bottom: 1px solid #E0E0E0; /* Adiciona uma linha sutil abaixo das abas */
    }

    div.stTabs [data-baseweb="tab-list"] { 
        /* Contêiner da lista de abas (onde ficam os "botões" das abas) */
        gap: 2px; /* Espaçamento entre os títulos das abas */
        /* display: flex; /* Garante alinhamento, geralmente já é padrão */
        /* justify-content: flex-start; /* Alinha as abas à esquerda */
    }

    div.stTabs [data-baseweb="tab"] { 
        /* Estilo para cada título/botão de aba individual */
        height: 40px;
        white-space: pre-wrap;
        background-color: #F0F2F6;       /* Cinza claro para ABA INATIVA (cor padrão do Streamlit) */
        border-radius: 4px 4px 0px 0px;   /* Cantos arredondados apenas no topo */
        padding: 10px 16px;               /* Ajuste o padding conforme necessário */
        margin-right: 2px;                /* Pequeno espaço à direita de cada aba inativa */
        color: #4F4F4F;                   /* Cor do texto para aba INATIVA (cinza escuro) */
        border: 1px solid transparent;    /* Borda transparente para abas inativas */
        border-bottom: none;              /* Sem borda inferior para abas inativas */
        transition: background-color 0.2s ease-in-out, color 0.2s ease-in-out; /* Transição suave */
    }
    div.stTabs [data-baseweb="tab"]:hover {
        background-color: #E0E0E0;       /* Cor de fundo um pouco mais escura no hover da aba inativa */
        color: #1E1E1E;                   /* Cor do texto mais escura no hover da aba inativa */
    }

    div.stTabs [aria-selected="true"] { 
        /* Estilo para a ABA ATIVA */
        background-color: #FFFFFF;       /* Branco para ABA ATIVA (cor padrão do Streamlit) */
        color: #0068C9;                   /* Cor do texto para aba ATIVA (azul primário do Streamlit) */
                                          /* Alternativa: color: #1E1E1E; para texto preto/escuro */
        /* font-weight: 600; /* Opcional: deixar o texto da aba ativa um pouco mais destacado */
        border: 1px solid #E0E0E0;       /* Borda para a aba ativa, para destacá-la do conteúdo */
        border-bottom: 1px solid #FFFFFF; /* "Corta" a borda inferior para conectar com o painel */
        box-shadow: none;                 /* Remove qualquer sombra padrão se houver */
    }

    /* Estilo para o painel de conteúdo da aba (opcional) */
    /* div[data-baseweb="tab-panel"] { */
    /* padding-top: 20px; /* Adiciona um espaço acima do conteúdo da aba */
    /* } */

</style>
""", unsafe_allow_html=True)

cols_nav = st.columns(len(PAGES))
for i, page_name in enumerate(PAGES):
    if cols_nav[i].button(page_name, key=f"nav_btn_{page_name}"):
        st.session_state.current_page = page_name
        st.rerun() # Força o rerender para atualizar a página

st.markdown("---") # Linha divisória após a navegação

# --- Conteúdo da Página Selecionada ---

if st.session_state.current_page == "Gerador de Propostas":
    st.title("Gerador de Propostas")

    # --- Funções de Callback e Inicialização de Estado (Específicas desta página) ---
    def update_offer_related_fields_gp(): # Renomeado para evitar conflito se houver outras
        selected_key = st.session_state.gp_tipo_oferta_selector # Chave específica da página
        if selected_key in OFFER_TYPES_DETAILS:
            st.session_state.gp_form_inputs["tipo_oferta"] = selected_key
            st.session_state.gp_form_inputs["tipo_oferta_ext"] = OFFER_TYPES_DETAILS[selected_key]["extenso"]
        else: 
            st.session_state.gp_form_inputs["tipo_oferta"] = selected_key
            st.session_state.gp_form_inputs["tipo_oferta_ext"] = "Não especificado"

    if 'gp_form_inputs' not in st.session_state: # Usar prefixo para evitar conflitos de estado
        st.session_state.gp_form_inputs = {
            "emissora": "NOME DA SUA SECURITIZADORA AQUI S.A.", "cnpj_emissora": "00.000.000/0001-00",
            "copia_nome": "", "copia_email": "", 
            "devedora": "NOME DA EMPRESA DEVEDORA", "cnpj_devedora": "11.111.111/0001-11",
            "endereco_devedora": "Rua Exemplo Devedora", "end_num_devedora": "123",
            "bairro_devedora": "Bairro Exemplo", "cidade_devedora": "Cidade Exemplo",
            "estado_devedora": "UF", "cep_devedora": "00000-000",
            "tipo_oferta": OFFER_TYPE_OPTIONS[0], 
            "tipo_oferta_ext": OFFER_TYPES_DETAILS[OFFER_TYPE_OPTIONS[0]]["extenso"], 
            "valor_total_str": "10000000,00",
            "remuneracao_str": "0,50",
            "prazo": "XX (XXXX) anos",
            "lastro": "Cédulas de Crédito Imobiliário (“CCI”)",
            "destinacao": "Ex: Reembolso de custos e despesas...",
            "remuneracao_titulo": "CDI + X,XX% a.a.",
            "amortizacao_principal": "Ex: Ao final do prazo de vencimento",
            "pagamento_juros": "Ex: Mensalmente, conforme Tabela Price",
            "garantias": "1) Fiança dos acionistas...\n2) Alienação Fiduciária...",
            "uso_recursos_debenture": "Descrição do uso dos recursos captados pela debênture",
            "cotas_fidc": "Ex: Cotas Seniores, Cotas Subordinadas Mezanino, Cotas Subordinadas Júnior",
            "serie_cotas_fidc": "Ex: Única",
            "gestor_fidc": "Nome do Gestor do FIDC",
            "administrador_fidc": "Nome do Administrador do FIDC",
            "custodiante_fidc": "Nome do Custodiante do FIDC",
            "comissao_performance_existe": True,
            "signatario_nome": "NOME DO DIRETOR DA SECURITIZADORA",
            "signatario_email": "diretor@suasecuritizadora.com",
        }

    if "gp_tipo_oferta_selector" not in st.session_state: # Chave específica da página
        st.session_state.gp_tipo_oferta_selector = st.session_state.gp_form_inputs["tipo_oferta"]
    elif st.session_state.gp_tipo_oferta_selector != st.session_state.gp_form_inputs["tipo_oferta"]:
         st.session_state.gp_tipo_oferta_selector = st.session_state.gp_form_inputs["tipo_oferta"]

    # --- Layout da Página "Gerador de Propostas" ---
    # A sidebar agora é parte desta "página"
    with st.sidebar:
        st.header("Gerador de Propostas") # Título da sidebar
        st.subheader("1. Selecione o Modelo")
        uploaded_template = st.file_uploader("Escolha o arquivo de modelo (.docx)", type="docx", label_visibility="collapsed", key="gp_template_uploader")

        st.subheader("2. Preencha os Dados da Proposta")
        with st.expander("Dados da Emissora e Signatário", expanded=False):
            st.session_state.gp_form_inputs["emissora"] = st.text_input("Emissora:", value=st.session_state.gp_form_inputs["emissora"], key="gp_emissora")
            st.session_state.gp_form_inputs["cnpj_emissora"] = st.text_input("CNPJ Emissora:", value=st.session_state.gp_form_inputs["cnpj_emissora"], key="gp_cnpj_emissora")
            st.session_state.gp_form_inputs["signatario_nome"] = st.text_input("Nome do Signatário (Emissora):", value=st.session_state.gp_form_inputs["signatario_nome"], key="gp_signatario_nome")
            st.session_state.gp_form_inputs["signatario_email"] = st.text_input("E-mail do Signatário (Emissora):", value=st.session_state.gp_form_inputs["signatario_email"], key="gp_signatario_email")

        with st.expander("Pessoas em Cópia (Opcional)", expanded=False):
            st.session_state.gp_form_inputs["copia_nome"] = st.text_input("Nome (Em Cópia):", value=st.session_state.gp_form_inputs["copia_nome"], key="gp_copia_nome")
            st.session_state.gp_form_inputs["copia_email"] = st.text_input("E-mail (Em Cópia):", value=st.session_state.gp_form_inputs["copia_email"], key="gp_copia_email")
        
        st.subheader("3. Gerar Proposta")
        if st.button("Gerar Documento da Proposta", use_container_width=True, type="primary", key="gp_gerar_proposta_btn"):
            if uploaded_template is None:
                st.error("❌ Por favor, selecione um arquivo de modelo (.docx) primeiro.")
            else:
                with st.spinner("Gerando proposta... Por favor, aguarde."):
                    try:
                        inputs = st.session_state.gp_form_inputs
                        data_to_replace, placeholders_to_bold, validation_info = prepare_document_data(inputs)

                        if validation_info["errors"]:
                            for error_msg in validation_info["errors"]:
                                st.error(f"⚠️ Erro de Entrada: {error_msg}")
                            # st.stop() # Não usar st.stop() dentro da sidebar se possível, pode dar comportamento estranho
                            # Em vez disso, apenas não prosseguir com a geração.
                        else: # Prossegue apenas se não houver erros críticos
                            if validation_info["warnings"]:
                                for warning_msg in validation_info["warnings"]:
                                    st.warning(f"🔔 Aviso: {warning_msg}")
                            
                            comissao_perf_existe_input = inputs.get("comissao_performance_existe", True)
                            template_file_bytes = BytesIO(uploaded_template.getvalue())
                            
                            generated_doc_io = generate_docx(
                                template_file_bytes, 
                                data_to_replace, 
                                placeholders_to_bold, 
                                comissao_perf_existe_input
                            )
                            
                            output_filename = f"Proposta Coordenação - {inputs['tipo_oferta'].replace(' ','_')} {inputs['devedora'].replace(' ','_')}.docx"
                            
                            st.success(f"✅ Proposta '{output_filename}' gerada!")
                            st.download_button(
                                label="⬇️ Baixar Proposta Gerada",
                                data=generated_doc_io,
                                file_name=output_filename,
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                use_container_width=True,
                                key="gp_download_btn"
                            )
                    except Exception as e:
                        st.error(f"❌ Ocorreu um erro crítico ao gerar a proposta: {e}")
                        st.error(f"Detalhes do erro: {traceback.format_exc()}")


    # Conteúdo principal da página "Gerador de Propostas" (abas, etc.)
    gp_tab_operacao, gp_tab_devedora = st.tabs(["Detalhes da Operação", "Informações da Devedora"])

    with gp_tab_devedora:
        st.subheader("Informações da Empresa Devedora")
        st.session_state.gp_form_inputs["cnpj_devedora"] = st.text_input(
            "CNPJ Devedora:",
            value=st.session_state.gp_form_inputs["cnpj_devedora"],
            key="gp_cnpj_devedora_display" 
        )

        if st.button("Buscar Dados do CNPJ", key="gp_buscar_cnpj_devedora_btn", use_container_width=True):
            cnpj_digitado = st.session_state.gp_form_inputs["cnpj_devedora"]
            if cnpj_digitado:
                with st.spinner(f"Buscando dados para o CNPJ {cnpj_digitado}..."):
                    dados_api = consultar_cnpj(cnpj_digitado) 
                
                if dados_api:
                    st.success("Dados encontrados e atualizados!")
                    st.session_state.gp_form_inputs["devedora"] = dados_api.get("company", {}).get("name", st.session_state.gp_form_inputs["devedora"])
                    address_data = dados_api.get("address", {})
                    st.session_state.gp_form_inputs["endereco_devedora"] = address_data.get("street", st.session_state.gp_form_inputs["endereco_devedora"])
                    st.session_state.gp_form_inputs["end_num_devedora"] = address_data.get("number", st.session_state.gp_form_inputs["end_num_devedora"])
                    st.session_state.gp_form_inputs["bairro_devedora"] = address_data.get("district", st.session_state.gp_form_inputs["bairro_devedora"])
                    st.session_state.gp_form_inputs["cidade_devedora"] = address_data.get("city", st.session_state.gp_form_inputs["cidade_devedora"])
                    st.session_state.gp_form_inputs["estado_devedora"] = address_data.get("state", st.session_state.gp_form_inputs["estado_devedora"])
                    unformatted_cep = address_data.get("zip")
                    if unformatted_cep:
                        st.session_state.gp_form_inputs["cep_devedora"] = format_cep(str(unformatted_cep))
                    st.experimental_rerun() 
                else:
                    st.warning(f"Nenhum dado encontrado para o CNPJ {cnpj_digitado} ou API indisponível. Por favor, preencha manualmente.")
            else:
                st.error("Por favor, digite um CNPJ para buscar.")

        gp_col_dev1, gp_col_dev2 = st.columns(2)
        with gp_col_dev1:
            st.session_state.gp_form_inputs["devedora"] = st.text_input("Devedora:", value=st.session_state.gp_form_inputs["devedora"], key="gp_devedora_input")
            st.session_state.gp_form_inputs["endereco_devedora"] = st.text_input("Endereço Devedora (Rua):", value=st.session_state.gp_form_inputs["endereco_devedora"], key="gp_endereco_devedora_input")
            st.session_state.gp_form_inputs["end_num_devedora"] = st.text_input("Número End. Devedora:", value=st.session_state.gp_form_inputs["end_num_devedora"], key="gp_end_num_devedora_input")
        with gp_col_dev2:
            st.session_state.gp_form_inputs["bairro_devedora"] = st.text_input("Bairro Devedora:", value=st.session_state.gp_form_inputs["bairro_devedora"], key="gp_bairro_devedora_input")
            st.session_state.gp_form_inputs["cidade_devedora"] = st.text_input("Cidade Devedora:", value=st.session_state.gp_form_inputs["cidade_devedora"], key="gp_cidade_devedora_input")
            st.session_state.gp_form_inputs["estado_devedora"] = st.text_input("Estado Devedora (UF):", value=st.session_state.gp_form_inputs["estado_devedora"], max_chars=2, key="gp_estado_devedora_input")
            st.session_state.gp_form_inputs["cep_devedora"] = st.text_input("CEP Devedora:", value=st.session_state.gp_form_inputs["cep_devedora"], key="gp_cep_devedora_input")
        
    with gp_tab_operacao:
        st.subheader("Detalhes da Operação")
        selected_offer_key_gp = st.selectbox(
            "Tipo da Oferta:",
            options=OFFER_TYPE_OPTIONS, 
            key="gp_tipo_oferta_selector", 
            on_change=update_offer_related_fields_gp
        )
        st.text_input("Tipo da Oferta (Extenso):", value=st.session_state.gp_form_inputs["tipo_oferta_ext"], key="gp_tipo_oferta_ext_display", disabled=True)

        gp_op_col1, gp_op_col2 = st.columns(2)
        with gp_op_col1:
            st.session_state.gp_form_inputs["valor_total_str"] = st.text_input("Valor Total da Operação (Ex: 10.000.000,00):", value=st.session_state.gp_form_inputs["valor_total_str"], key="gp_valor_total_str")
            st.session_state.gp_form_inputs["prazo"] = st.text_input("Prazo da Operação:", value=st.session_state.gp_form_inputs["prazo"], key="gp_prazo")
        with gp_op_col2:
            st.session_state.gp_form_inputs["remuneracao_str"] = st.text_input(
                "Remuneração da Estruturação (% Ex: 0,50 ou 2):",
                value=st.session_state.gp_form_inputs["remuneracao_str"],
                key="gp_remuneracao_str"
            )

        performance_options_map_gp = {"Sim": True, "Não": False}
        performance_labels_gp = list(performance_options_map_gp.keys())
        default_index_performance_gp = 0 if st.session_state.gp_form_inputs.get("comissao_performance_existe", True) else 1

        selected_performance_label_gp = st.selectbox(
            "Haverá Comissão de Performance (impacta item 6.2 da proposta)?",
            options=performance_labels_gp,
            index=default_index_performance_gp,
            key="gp_comissao_performance_selector" 
        )
        st.session_state.gp_form_inputs["comissao_performance_existe"] = performance_options_map_gp[selected_performance_label_gp]

        st.markdown("---")
        st.write(f"**Detalhes Específicos para {st.session_state.gp_form_inputs['tipo_oferta']}:**")
        
        current_selected_offer_for_fields_gp = st.session_state.gp_form_inputs["tipo_oferta"]
        relevant_fields_for_offer_gp = OFFER_TYPES_DETAILS.get(current_selected_offer_for_fields_gp, {}).get("fields", [])
        
        for field_key in relevant_fields_for_offer_gp:
            default_value = st.session_state.gp_form_inputs.get(field_key, "") 
            label = field_key.replace("_", " ").capitalize() + ":"
            
            if field_key == "lastro": label = "Lastro da Operação:"
            elif field_key == "remuneracao_titulo": label = "Remuneração do Título:"
            elif field_key == "amortizacao_principal": label = "Amortização do Principal:"
            elif field_key == "pagamento_juros": label = "Pagamento de Juros:"
            elif field_key == "destinacao":
                label = "Destinação dos Recursos:"
                st.session_state.gp_form_inputs[field_key] = st.text_area(label, value=default_value, height=100, key=f"gp_input_{field_key}")
                continue
            elif field_key == "garantias":
                label = "Garantias da Operação (uma por linha):"
                st.session_state.gp_form_inputs[field_key] = st.text_area(label, value=default_value, height=100, key=f"gp_input_{field_key}")
                continue
            elif field_key == "cotas_fidc": label = "Estrutura das Cotas do FIDC:"
            elif field_key == "serie_cotas_fidc": label = "Série das Cotas:"
            elif field_key == "gestor_fidc": label = "Gestor do FIDC:"
            elif field_key == "administrador_fidc": label = "Administrador do FIDC:"
            elif field_key == "custodiante_fidc": label = "Custodiante do FIDC:"
            elif field_key == "uso_recursos_debenture":
                label = "Uso Específico dos Recursos (Debênture):"
                st.session_state.gp_form_inputs[field_key] = st.text_area(label, value=default_value, height=100, key=f"gp_input_{field_key}")
                continue
            
            st.session_state.gp_form_inputs[field_key] = st.text_input(label, value=default_value, key=f"gp_input_{field_key}")

elif st.session_state.current_page == "Dashboard":
    st.title("Dashboard")
    st.write("Bem-vindo ao Dashboard!")
    st.write("Esta página ainda está em desenvolvimento.")
    # Adicione aqui o conteúdo do seu Dashboard

elif st.session_state.current_page == "Configurações":
    st.title("Configurações")
    st.write("Página de Configurações.")
    st.write("Esta página ainda está em desenvolvimento.")
    # Adicione aqui as opções de configuração

elif st.session_state.current_page == "Ajuda":
    st.title("Ajuda & Suporte")
    st.write("Página de Ajuda.")
    st.write("Consulte a documentação ou entre em contato para suporte.")
    # Adicione aqui informações de ajuda