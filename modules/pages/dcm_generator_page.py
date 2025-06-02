import streamlit as st
from io import BytesIO
import traceback

# Importações dos módulos utilitários e de lógica de negócios do DCM
from .. import api
from .. import dcm_core_logic
from .. import common_processing_utils

def render_dcm_page():
    # --- Funções de Callback e Inicialização de Estado (Específicas desta página DCM) ---
    def update_offer_related_fields_dcm():
        selected_key = st.session_state.dcm_tipo_oferta_selector
        if selected_key in dcm_core_logic.OFFER_TYPES_DETAILS:
            st.session_state.dcm_form_inputs["tipo_oferta"] = selected_key
            st.session_state.dcm_form_inputs["tipo_oferta_ext"] = dcm_core_logic.OFFER_TYPES_DETAILS[selected_key]["extenso"]
        else:
            st.session_state.dcm_form_inputs["tipo_oferta"] = selected_key
            st.session_state.dcm_form_inputs["tipo_oferta_ext"] = "Não especificado"

    if 'dcm_form_inputs' not in st.session_state:
        st.session_state.dcm_form_inputs = {
            "emissora": "NOME DA SUA SECURITIZADORA AQUI S.A.", "cnpj_emissora": "00.000.000/0001-00",
            "copia_nome": "", "copia_email": "",
            "devedora": "NOME DA EMPRESA DEVEDORA", "cnpj_devedora": "11.111.111/0001-11",
            "endereco_devedora": "Rua Exemplo Devedora", "end_num_devedora": "123",
            "bairro_devedora": "Bairro Exemplo", "cidade_devedora": "Cidade Exemplo",
            "estado_devedora": "UF", "cep_devedora": "00000-000",
            "tipo_oferta": dcm_core_logic.OFFER_TYPE_OPTIONS[0],
            "tipo_oferta_ext": dcm_core_logic.OFFER_TYPES_DETAILS[dcm_core_logic.OFFER_TYPE_OPTIONS[0]]["extenso"],
            "valor_total_str": "10000000,00",
            "remuneracao_str": "0,50", # Para DCM, é percentual
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

    if "dcm_tipo_oferta_selector" not in st.session_state:
        st.session_state.dcm_tipo_oferta_selector = st.session_state.dcm_form_inputs["tipo_oferta"]
    elif st.session_state.dcm_tipo_oferta_selector != st.session_state.dcm_form_inputs["tipo_oferta"]:
         st.session_state.dcm_tipo_oferta_selector = st.session_state.dcm_form_inputs["tipo_oferta"]

    # --- Layout da Página "Gerador de Propostas DCM" ---
    with st.sidebar: # A sidebar continua aqui, mas específica para DCM
        st.header("Gerador DCM")
        st.subheader("1. Selecione o Modelo")
        uploaded_template_dcm = st.file_uploader("Escolha o arquivo de modelo (.docx)", type="docx", label_visibility="collapsed", key="dcm_template_uploader")

        st.subheader("2. Preencha os Dados")
        with st.expander("Dados da Emissora e Signatário", expanded=False):
            st.session_state.dcm_form_inputs["emissora"] = st.text_input("Emissora:", value=st.session_state.dcm_form_inputs["emissora"], key="dcm_emissora")
            st.session_state.dcm_form_inputs["cnpj_emissora"] = st.text_input("CNPJ Emissora:", value=st.session_state.dcm_form_inputs["cnpj_emissora"], key="dcm_cnpj_emissora")
            st.session_state.dcm_form_inputs["signatario_nome"] = st.text_input("Nome do Signatário (Emissora):", value=st.session_state.dcm_form_inputs["signatario_nome"], key="dcm_signatario_nome")
            st.session_state.dcm_form_inputs["signatario_email"] = st.text_input("E-mail do Signatário (Emissora):", value=st.session_state.dcm_form_inputs["signatario_email"], key="dcm_signatario_email")

        with st.expander("Pessoas em Cópia (Opcional)", expanded=False):
            st.session_state.dcm_form_inputs["copia_nome"] = st.text_input("Nome (Em Cópia):", value=st.session_state.dcm_form_inputs["copia_nome"], key="dcm_copia_nome")
            st.session_state.dcm_form_inputs["copia_email"] = st.text_input("E-mail (Em Cópia):", value=st.session_state.dcm_form_inputs["copia_email"], key="dcm_copia_email")
        
        st.subheader("3. Gerar Proposta")
        if st.button("Gerar Documento", use_container_width=True, type="primary", key="dcm_gerar_proposta_btn"):
            if uploaded_template_dcm is None:
                st.error("❌ Por favor, selecione um arquivo de modelo (.docx) para DCM.")
            else:
                with st.spinner("Gerando proposta DCM... Por favor, aguarde."):
                    try:
                        inputs = st.session_state.dcm_form_inputs
                        # Usar a função de preparo de dados do dcm_core_logic
                        data_to_replace, placeholders_to_bold, validation_info = dcm_core_logic.prepare_document_data(inputs)

                        if validation_info["errors"]:
                            for error_msg in validation_info["errors"]:
                                st.error(f"⚠️ Erro de Entrada (DCM): {error_msg}")
                        else:
                            if validation_info["warnings"]:
                                for warning_msg in validation_info["warnings"]:
                                    st.warning(f"🔔 Aviso (DCM): {warning_msg}")
                            
                            comissao_perf_existe_input = inputs.get("comissao_performance_existe", True)
                            template_file_bytes = BytesIO(uploaded_template_dcm.getvalue())
                            
                            # Usar a função de geração de DOCX específica para DCM
                            generated_doc_io = common_processing_utils.generate_docx_dcm(
                                template_file_bytes, 
                                data_to_replace, 
                                placeholders_to_bold, 
                                comissao_perf_existe_input
                            )
                            
                            output_filename = f"Proposta_DCM - {inputs['tipo_oferta'].replace(' ','_')} {inputs['devedora'].replace(' ','_')}.docx"
                            
                            st.success(f"✅ Proposta DCM '{output_filename}' gerada!")
                            st.download_button(
                                label="⬇️ Baixar Proposta DCM Gerada",
                                data=generated_doc_io,
                                file_name=output_filename,
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                use_container_width=True,
                                key="dcm_download_btn"
                            )
                    except Exception as e:
                        st.error(f"❌ Ocorreu um erro crítico ao gerar a proposta DCM: {e}")
                        st.error(f"Detalhes do erro: {traceback.format_exc()}")

    # Conteúdo principal da página "Gerador de Propostas DCM" (abas, etc.)
    dcm_tab_operacao, dcm_tab_devedora = st.tabs(["Detalhes da Operação", "Informações da Devedora"])

    with dcm_tab_devedora:
        st.subheader("Informações da Empresa Devedora")
        st.session_state.dcm_form_inputs["cnpj_devedora"] = st.text_input(
            "CNPJ Devedora:",
            value=st.session_state.dcm_form_inputs["cnpj_devedora"],
            key="dcm_cnpj_devedora_display" 
        )

        if st.button("Buscar Dados do CNPJ", key="dcm_buscar_cnpj_devedora_btn", use_container_width=True):
            cnpj_digitado = st.session_state.dcm_form_inputs["cnpj_devedora"]
            if cnpj_digitado:
                with st.spinner(f"Buscando dados para o CNPJ {cnpj_digitado}..."):
                    dados_api = api.consultar_cnpj(cnpj_digitado)
                
                if dados_api and "erro" not in dados_api: # Verifica se não houve erro na API
                    st.success("Dados encontrados e atualizados!")
                    st.session_state.dcm_form_inputs["devedora"] = dados_api.get("company", {}).get("name", st.session_state.dcm_form_inputs["devedora"])
                    address_data = dados_api.get("address", {})
                    st.session_state.dcm_form_inputs["endereco_devedora"] = address_data.get("street", st.session_state.dcm_form_inputs["endereco_devedora"])
                    st.session_state.dcm_form_inputs["end_num_devedora"] = address_data.get("number", st.session_state.dcm_form_inputs["end_num_devedora"])
                    st.session_state.dcm_form_inputs["bairro_devedora"] = address_data.get("district", st.session_state.dcm_form_inputs["bairro_devedora"])
                    st.session_state.dcm_form_inputs["cidade_devedora"] = address_data.get("city", st.session_state.dcm_form_inputs["cidade_devedora"])
                    st.session_state.dcm_form_inputs["estado_devedora"] = address_data.get("state", st.session_state.dcm_form_inputs["estado_devedora"])
                    unformatted_cep = address_data.get("zip")
                    if unformatted_cep:
                        st.session_state.dcm_form_inputs["cep_devedora"] = dcm_core_logic.format_cep(str(unformatted_cep))
                    st.rerun() # Para atualizar os campos na UI
                else:
                    api_error_msg = dados_api.get("erro", "API indisponível ou CNPJ não encontrado.") if dados_api else "Falha na consulta à API."
                    st.warning(f"Nenhum dado encontrado para o CNPJ {cnpj_digitado} ou API indisponível. ({api_error_msg}). Por favor, preencha manualmente.")
            else:
                st.error("Por favor, digite um CNPJ para buscar.")

        dcm_col_dev1, dcm_col_dev2 = st.columns(2)
        with dcm_col_dev1:
            st.session_state.dcm_form_inputs["devedora"] = st.text_input("Devedora:", value=st.session_state.dcm_form_inputs["devedora"], key="dcm_devedora_input")
            st.session_state.dcm_form_inputs["endereco_devedora"] = st.text_input("Endereço Devedora (Rua):", value=st.session_state.dcm_form_inputs["endereco_devedora"], key="dcm_endereco_devedora_input")
            st.session_state.dcm_form_inputs["end_num_devedora"] = st.text_input("Número End. Devedora:", value=st.session_state.dcm_form_inputs["end_num_devedora"], key="dcm_end_num_devedora_input")
        with dcm_col_dev2:
            st.session_state.dcm_form_inputs["bairro_devedora"] = st.text_input("Bairro Devedora:", value=st.session_state.dcm_form_inputs["bairro_devedora"], key="dcm_bairro_devedora_input")
            st.session_state.dcm_form_inputs["cidade_devedora"] = st.text_input("Cidade Devedora:", value=st.session_state.dcm_form_inputs["cidade_devedora"], key="dcm_cidade_devedora_input")
            st.session_state.dcm_form_inputs["estado_devedora"] = st.text_input("Estado Devedora (UF):", value=st.session_state.dcm_form_inputs["estado_devedora"], max_chars=2, key="dcm_estado_devedora_input")
            st.session_state.dcm_form_inputs["cep_devedora"] = st.text_input("CEP Devedora:", value=st.session_state.dcm_form_inputs["cep_devedora"], key="dcm_cep_devedora_input")
        
    with dcm_tab_operacao:
        st.subheader("Detalhes da Operação")
        selected_offer_key_dcm = st.selectbox(
            "Tipo da Oferta:",
            options=dcm_core_logic.OFFER_TYPE_OPTIONS, 
            key="dcm_tipo_oferta_selector", 
            on_change=update_offer_related_fields_dcm
        )
        st.text_input("Tipo da Oferta (Extenso):", value=st.session_state.dcm_form_inputs["tipo_oferta_ext"], key="dcm_tipo_oferta_ext_display", disabled=True)

        dcm_op_col1, dcm_op_col2 = st.columns(2)
        with dcm_op_col1:
            st.session_state.dcm_form_inputs["valor_total_str"] = st.text_input("Valor Total da Operação:", value=st.session_state.dcm_form_inputs["valor_total_str"], key="dcm_valor_total_str")
            st.session_state.dcm_form_inputs["prazo"] = st.text_input("Prazo da Operação:", value=st.session_state.dcm_form_inputs["prazo"], key="dcm_prazo")
        with dcm_op_col2:
            st.session_state.dcm_form_inputs["remuneracao_str"] = st.text_input(
                "Remuneração da Estruturação (%):", #
                value=st.session_state.dcm_form_inputs["remuneracao_str"],
                key="dcm_remuneracao_str"
            )

        performance_options_map_dcm = {"Sim": True, "Não": False}
        performance_labels_dcm = list(performance_options_map_dcm.keys())
        default_index_performance_dcm = 0 if st.session_state.dcm_form_inputs.get("comissao_performance_existe", True) else 1

        selected_performance_label_dcm = st.selectbox(
            "Haverá Comissão de Performance (impacta item 6.2 da proposta DCM)?",
            options=performance_labels_dcm,
            index=default_index_performance_dcm,
            key="dcm_comissao_performance_selector" 
        )
        st.session_state.dcm_form_inputs["comissao_performance_existe"] = performance_options_map_dcm[selected_performance_label_dcm]

        st.markdown("---")
        st.write(f"**Detalhes Específicos para {st.session_state.dcm_form_inputs['tipo_oferta']} (DCM):**")
        
        current_selected_offer_for_fields_dcm = st.session_state.dcm_form_inputs["tipo_oferta"]
        relevant_fields_for_offer_dcm = dcm_core_logic.OFFER_TYPES_DETAILS.get(current_selected_offer_for_fields_dcm, {}).get("fields", [])
        
        for field_key in relevant_fields_for_offer_dcm:
            default_value = st.session_state.dcm_form_inputs.get(field_key, "") 
            label = field_key.replace("_", " ").capitalize() + " (DCM):"
            
            # Adaptação dos labels conforme o app.py original do GitHub
            if field_key == "lastro": label = "Lastro da Operação:"
            elif field_key == "remuneracao_titulo": label = "Remuneração do Título:"
            elif field_key == "amortizacao_principal": label = "Amortização do Principal:"
            elif field_key == "pagamento_juros": label = "Pagamento de Juros:"
            elif field_key == "destinacao":
                label = "Destinação dos Recursos:"
                st.session_state.dcm_form_inputs[field_key] = st.text_area(label, value=default_value, height=100, key=f"dcm_input_{field_key}")
                continue
            elif field_key == "garantias":
                label = "Garantias da Operação (uma por linha):"
                st.session_state.dcm_form_inputs[field_key] = st.text_area(label, value=default_value, height=100, key=f"dcm_input_{field_key}")
                continue
            elif field_key == "cotas_fidc": label = "Estrutura das Cotas do FIDC:"
            elif field_key == "serie_cotas_fidc": label = "Série das Cotas:"
            elif field_key == "gestor_fidc": label = "Gestor do FIDC:"
            elif field_key == "administrador_fidc": label = "Administrador do FIDC:"
            elif field_key == "custodiante_fidc": label = "Custodiante do FIDC:"
            elif field_key == "uso_recursos_debenture":
                label = "Uso Específico dos Recursos (Debênture):"
                st.session_state.dcm_form_inputs[field_key] = st.text_area(label, value=default_value, height=100, key=f"dcm_input_{field_key}")
                continue
            
            st.session_state.dcm_form_inputs[field_key] = st.text_input(label, value=default_value, key=f"dcm_input_{field_key}")