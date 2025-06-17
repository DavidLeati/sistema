# proposal_system/ui/dcm_page.py
import streamlit as st
from io import BytesIO
import traceback

from external_apis import cnpj_api
from core import dcm_logic
from document_processing import document_generator
from shared_utils import formatting_utils
from config import configs

def render_dcm_page():
    def sync_comissao_performance_checkbox():
        """
        Esta função é chamada AUTOMATICAMENTE quando o checkbox muda de estado.
        Ela sincroniza o estado do widget (armazenado pela sua 'key')
        com a nossa variável no dicionário do formulário.
        """
        st.session_state.dcm_form_inputs["comissao_performance_existe"] = st.session_state.dcm_comissao_performance_chk
 
    # --- Inicialização do Session State para os artefatos gerados ---
    if "dcm_generated_doc_io" not in st.session_state:
        st.session_state.dcm_generated_doc_io = None
    if "dcm_output_filename_docx" not in st.session_state:
        st.session_state.dcm_output_filename_docx = None
    if "dcm_process_complete" not in st.session_state: # Flag para controlar exibição
        st.session_state.dcm_process_complete = False
    if "dcm_error_message" not in st.session_state:
        st.session_state.dcm_error_message = None

    def update_offer_related_fields_dcm():
    # Pega a nova seleção
        selected_key = st.session_state.dcm_tipo_oferta_selector
        
        if selected_key in configs.DCM_OFFER_TYPES_DETAILS:
            # Atualiza os valores básicos do tipo de oferta
            st.session_state.dcm_form_inputs["tipo_oferta"] = selected_key
            st.session_state.dcm_form_inputs["tipo_oferta_ext"] = configs.DCM_OFFER_TYPES_DETAILS[selected_key]["extenso"]

            # --- LÓGICA DE LIMPEZA ADICIONADA ---
            # Lista de todos os campos que podem ser opcionais
            all_optional_fields = ["lastro", "uso_recursos_debenture", "covenants"]
            
            # Pega a lista de campos que são relevantes para a nova seleção
            relevant_fields = configs.DCM_OFFER_TYPES_DETAILS[selected_key].get("fields", [])
            
            # Itera sobre todos os campos opcionais e limpa aqueles que NÃO são relevantes
            for field in all_optional_fields:
                if field not in relevant_fields:
                    st.session_state.dcm_form_inputs[field] = ""
            # --- FIM DA LÓGICA DE LIMPEZA ---
                    
        else:
            st.session_state.dcm_form_inputs["tipo_oferta"] = ""
            st.session_state.dcm_form_inputs["tipo_oferta_ext"] = ""

    if 'dcm_form_inputs' not in st.session_state: #
        st.session_state.dcm_form_inputs = { #
            "emissora": "NOME DA SUA SECURITIZADORA AQUI S.A.", "cnpj_emissora": "00.000.000/0001-00", #
            "copia_nome": "", "copia_email": "", #
            "devedora": "NOME DA EMPRESA DEVEDORA", "cnpj_devedora": "11.111.111/0001-11", #
            "endereco_devedora": "Rua Exemplo Devedora", "end_num_devedora": "123", #
            "bairro_devedora": "Bairro Exemplo", "cidade_devedora": "Cidade Exemplo", #
            "estado_devedora": "UF", "cep_devedora": "00000-000", #
            "tipo_oferta": list(configs.DCM_OFFER_TYPES_DETAILS.keys())[0], #
            "tipo_oferta_ext": configs.DCM_OFFER_TYPES_DETAILS[list(configs.DCM_OFFER_TYPES_DETAILS.keys())[0]]["extenso"], #
            "valor_total_str": "10000000,00", "remuneracao_str": "0,50", "prazo": "XX (XXXX) anos", #
            "lastro": "Cédulas de Crédito Imobiliário (“CCI”)", "destinacao": "Ex: Reembolso de custos e despesas...", #
            "remuneracao_titulo": "CDI + X,XX% a.a.", "amortizacao_principal": "Ex: Ao final do prazo de vencimento", #
            "pagamento_juros": "Ex: Mensalmente, conforme Tabela Price", "garantias": "1) Fiança dos acionistas...\n2) Alienação Fiduciária...", #
            "uso_recursos_debenture": "Descrição do uso dos recursos captados pela debênture", #
            "cotas_fidc": "Ex: Cotas Seniores, Cotas Subordinadas Mezanino, Cotas Subordinadas Júnior", "serie_cotas_fidc": "Ex: Única", #
            "gestor_fidc": "Nome do Gestor do FIDC", "administrador_fidc": "Nome do Administrador do FIDC", #
            "custodiante_fidc": "Nome do Custodiante do FIDC", "comissao_performance_existe": True, #
            "signatario_nome": "NOME DO DIRETOR DA SECURITIZADORA", "signatario_email": "diretor@suasecuritizadora.com", #
            "manter_outro_instrumento": False, "tipo_secundario": ""
            }

    if "dcm_tipo_oferta_selector" not in st.session_state: #
        st.session_state.dcm_tipo_oferta_selector = st.session_state.dcm_form_inputs["tipo_oferta"] #
    elif st.session_state.dcm_tipo_oferta_selector != st.session_state.dcm_form_inputs["tipo_oferta"]: #
        st.session_state.dcm_tipo_oferta_selector = st.session_state.dcm_form_inputs["tipo_oferta"] #

    checkbox_visibility_key = "dcm_mostrar_dados_inputs_key" #

    if checkbox_visibility_key not in st.session_state: #
        st.session_state[checkbox_visibility_key] = True #

    with st.sidebar: #
        st.header("Gerador DCM") #
        st.subheader("- Selecione o Modelo -") #
        uploaded_template_dcm = st.file_uploader("Escolha o arquivo de modelo (.docx)", type="docx", label_visibility="collapsed", key="dcm_template_uploader") #

        st.subheader("- Preencha os Dados -")

        # 1. Checkbox agora está aqui, controlando apenas a seção abaixo dele.
        st.checkbox(
            "Adicionar Securitizadora?",
            key=checkbox_visibility_key
        )

        # 2. A visibilidade deste expander e a limpeza dos seus dados
        #    são controladas pelo checkbox.
        if st.session_state[checkbox_visibility_key]:
            with st.expander("Informações da Securitizadora", expanded=False):
                st.session_state.dcm_form_inputs["emissora"] = st.text_input("Emissora:", value=st.session_state.dcm_form_inputs["emissora"], key="dcm_emissora")
                st.session_state.dcm_form_inputs["cnpj_emissora"] = st.text_input("CNPJ Emissora:", value=st.session_state.dcm_form_inputs["cnpj_emissora"], key="dcm_cnpj_emissora")
                st.session_state.dcm_form_inputs["signatario_nome"] = st.text_input("Nome do Signatário (Emissora):", value=st.session_state.dcm_form_inputs["signatario_nome"], key="dcm_signatario_nome")
                st.session_state.dcm_form_inputs["signatario_email"] = st.text_input("E-mail do Signatário (Emissora):", value=st.session_state.dcm_form_inputs["signatario_email"], key="dcm_signatario_email")
        else:
            # Limpa os dados apenas da securitizadora se o checkbox for desmarcado.
            st.session_state.dcm_form_inputs["emissora"] = ""
            st.session_state.dcm_form_inputs["cnpj_emissora"] = ""
            st.session_state.dcm_form_inputs["signatario_nome"] = ""
            st.session_state.dcm_form_inputs["signatario_email"] = ""

        # 3. Este expander agora está sempre visível, independentemente do checkbox.
        with st.expander("Pessoas em Cópia", expanded=False):
            st.session_state.dcm_form_inputs["copia_nome"] = st.text_input("Nome (Em Cópia):", value=st.session_state.dcm_form_inputs["copia_nome"], key="dcm_copia_nome")


        st.subheader("- Gerar Proposta -") #
        if st.button("Gerar Documento", use_container_width=True, type="primary", key="dcm_gerar_proposta_btn"): #
            # Resetar estados anteriores ao iniciar nova geração
            st.session_state.dcm_process_complete = False
            st.session_state.dcm_generated_doc_io = None
            st.session_state.dcm_pdf_bytes_io = None
            st.session_state.dcm_output_filename_docx = None
            st.session_state.dcm_output_filename_pdf = None
            st.session_state.dcm_error_message = None
            st.session_state.dcm_pdf_conversion_error_message = None

            if uploaded_template_dcm is None: #
                st.error("❌ Por favor, selecione um arquivo de modelo (.docx) para DCM.") #
                st.session_state.dcm_process_complete = True # Indica que o processo (tentativa) terminou
            else:
                with st.spinner("Gerando proposta DCM... Por favor, aguarde."): #
                    try:
                        inputs = st.session_state.dcm_form_inputs #
                        data_to_replace, placeholders_to_bold, validation_info = dcm_logic.prepare_document_data(inputs) #

                        if validation_info["errors"]: #
                            for error_msg in validation_info["errors"]: #
                                st.error(f"⚠️ Erro de Entrada (DCM): {error_msg}") #
                            # Mesmo com erro de validação, marcamos como processo tentado
                            st.session_state.dcm_process_complete = True
                            # Não prossegue para geração se houver erros de validação
                            return # Sai da lógica do botão de geração

                        if validation_info["warnings"]: #
                            for warning_msg in validation_info["warnings"]: #
                                st.warning(f"🔔 Aviso (DCM): {warning_msg}") #

                        comissao_perf_existe_input = inputs.get("comissao_performance_existe", True) #
                        template_file_bytes = BytesIO(uploaded_template_dcm.getvalue()) #

                        generated_doc_io = document_generator.generate_dcm_document( #
                            template_file_bytes, data_to_replace, placeholders_to_bold, comissao_perf_existe_input #
                        )
                        st.session_state.dcm_generated_doc_io = generated_doc_io # Guarda no session_state

                        base_filename = f"Proposta_DCM - {inputs['tipo_oferta'].replace(' ','_')} {inputs['devedora'].replace(' ','_')}" #
                        st.session_state.dcm_output_filename_docx = f"{base_filename}.docx" #

                    except Exception as e: #
                        st.session_state.dcm_error_message = f"❌ Ocorreu um erro crítico ao gerar a proposta DCM: {e}\nDetalhes: {traceback.format_exc()}" #
                    finally:
                        st.session_state.dcm_process_complete = True # Marca que o processo (geração/conversão) terminou

        # --- Exibição dos resultados e botões de download (fora do if do botão "Gerar") ---
        # Isso garante que eles sejam re-renderizados mesmo após um clique em download
        if st.session_state.dcm_process_complete:
            if st.session_state.dcm_error_message:
                st.error(st.session_state.dcm_error_message)

            if st.session_state.dcm_generated_doc_io:
                st.success(f"✅ Proposta DCM '{st.session_state.dcm_output_filename_docx}' gerada!") #
                st.download_button( #
                    label="⬇️ Baixar Proposta DCM Gerada (.docx)",
                    data=st.session_state.dcm_generated_doc_io,
                    file_name=st.session_state.dcm_output_filename_docx,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", #
                    use_container_width=True,
                    key="dcm_download_btn_docx_final" # Chave única
                )

    # --- Restante da UI da página (abas, inputs, etc.) ---
    dcm_tab_operacao, dcm_tab_devedora = st.tabs(["Detalhes da Operação", "Informações da Devedora"]) #
    with dcm_tab_devedora: #
        st.subheader("Informações da Empresa Devedora") #
        st.session_state.dcm_form_inputs["cnpj_devedora"] = st.text_input( #
            "CNPJ Devedora:", value=st.session_state.dcm_form_inputs["cnpj_devedora"], key="dcm_cnpj_devedora_display" #
        )
        if st.button("Buscar Dados do CNPJ", key="dcm_buscar_cnpj_devedora_btn", use_container_width=True): #
            cnpj_digitado = st.session_state.dcm_form_inputs["cnpj_devedora"] #
            if cnpj_digitado: #
                with st.spinner(f"Buscando dados para o CNPJ {cnpj_digitado}..."): #
                    dados_api = cnpj_api.consultar_cnpj(cnpj_digitado) #
                if dados_api and "erro" not in dados_api: #
                    st.success("Dados encontrados e atualizados!") #
                    st.session_state.dcm_form_inputs["devedora"] = dados_api.get("company", {}).get("name", st.session_state.dcm_form_inputs["devedora"]) #
                    address_data = dados_api.get("address", {}) #
                    st.session_state.dcm_form_inputs["endereco_devedora"] = address_data.get("street", st.session_state.dcm_form_inputs["endereco_devedora"]) #
                    st.session_state.dcm_form_inputs["end_num_devedora"] = address_data.get("number", st.session_state.dcm_form_inputs["end_num_devedora"]) #
                    st.session_state.dcm_form_inputs["bairro_devedora"] = address_data.get("district", st.session_state.dcm_form_inputs["bairro_devedora"]) #
                    st.session_state.dcm_form_inputs["cidade_devedora"] = address_data.get("city", st.session_state.dcm_form_inputs["cidade_devedora"]) #
                    st.session_state.dcm_form_inputs["estado_devedora"] = address_data.get("state", st.session_state.dcm_form_inputs["estado_devedora"]) #
                    unformatted_cep = address_data.get("zip") #
                    if unformatted_cep: #
                        st.session_state.dcm_form_inputs["cep_devedora"] = formatting_utils.format_cep(str(unformatted_cep)) #
                    st.rerun() #
                else:
                    api_error_msg = dados_api.get("erro", "API indisponível ou CNPJ não encontrado.") if dados_api else "Falha na consulta à API." #
                    st.warning(f"Nenhum dado encontrado para o CNPJ {cnpj_digitado} ou API indisponível. ({api_error_msg}). Por favor, preencha manualmente.") #
            else:
                st.error("Por favor, digite um CNPJ para buscar.") #
        dcm_col_dev1, dcm_col_dev2 = st.columns(2) #
        with dcm_col_dev1: #
            st.session_state.dcm_form_inputs["devedora"] = st.text_input("Devedora:", value=st.session_state.dcm_form_inputs["devedora"], key="dcm_devedora_input") #
            st.session_state.dcm_form_inputs["endereco_devedora"] = st.text_input("Endereço Devedora (Rua):", value=st.session_state.dcm_form_inputs["endereco_devedora"], key="dcm_endereco_devedora_input") #
            st.session_state.dcm_form_inputs["end_num_devedora"] = st.text_input("Número End. Devedora:", value=st.session_state.dcm_form_inputs["end_num_devedora"], key="dcm_end_num_devedora_input") #
        with dcm_col_dev2: #
            st.session_state.dcm_form_inputs["bairro_devedora"] = st.text_input("Bairro Devedora:", value=st.session_state.dcm_form_inputs["bairro_devedora"], key="dcm_bairro_devedora_input") #
            st.session_state.dcm_form_inputs["cidade_devedora"] = st.text_input("Cidade Devedora:", value=st.session_state.dcm_form_inputs["cidade_devedora"], key="dcm_cidade_devedora_input") #
            st.session_state.dcm_form_inputs["estado_devedora"] = st.text_input("Estado Devedora (UF):", value=st.session_state.dcm_form_inputs["estado_devedora"], max_chars=2, key="dcm_estado_devedora_input") #
            st.session_state.dcm_form_inputs["cep_devedora"] = st.text_input("CEP Devedora:", value=st.session_state.dcm_form_inputs["cep_devedora"], key="dcm_cep_devedora_input") #

    with dcm_tab_operacao: #
        st.subheader("Detalhes da Operação") #
        selected_offer_key_dcm = st.selectbox( #
            "Tipo da Oferta:", options=configs.DCM_OFFER_TYPES_DETAILS, key="dcm_tipo_oferta_selector", on_change=update_offer_related_fields_dcm #
        )
        st.text_input("Tipo da Oferta (Extenso):", value=st.session_state.dcm_form_inputs["tipo_oferta_ext"], key="dcm_tipo_oferta_ext_display", disabled=True) #
        dcm_op_col1, dcm_op_col2 = st.columns(2) #
        with dcm_op_col1: #
            st.session_state.dcm_form_inputs["valor_total_str"] = st.text_input("Valor Total da Operação:", value=st.session_state.dcm_form_inputs["valor_total_str"], key="dcm_valor_total_str") #
            st.session_state.dcm_form_inputs["prazo"] = st.text_input("Prazo da Operação:", value=st.session_state.dcm_form_inputs["prazo"], key="dcm_prazo") #
        with dcm_op_col2: #
            st.session_state.dcm_form_inputs["remuneracao_str"] = st.text_input( #
                "Remuneração da Estruturação (%):", value=st.session_state.dcm_form_inputs["remuneracao_str"], key="dcm_remuneracao_str" #
            )

        if "dcm_comissao_performance_chk" not in st.session_state:
            st.session_state.dcm_comissao_performance_chk = st.session_state.dcm_form_inputs.get("comissao_performance_existe", True)

        # Agora, o checkbox não atribui valor diretamente. Ele chama a função on_change.
        st.checkbox(
            "Incluir Comissão de Performance?",
            key="dcm_comissao_performance_chk",
            on_change=sync_comissao_performance_checkbox
        )

        st.session_state.dcm_form_inputs["manter_outro_instrumento"] = st.checkbox(
            "Adicionar Cláusula de Outro Instrumento?",
            key="dcm_outro_instrumento_chk"
        )

        # Verifica o estado do checkbox que acabamos de definir
        if st.session_state.dcm_form_inputs["manter_outro_instrumento"]:
            # Se estiver MARCADO, mostra a área de texto para customização
            st.session_state.dcm_form_inputs["tipo_secundario"] = st.text_input(
                "Instrumento Secundário (plural):",
                value=st.session_state.dcm_form_inputs.get("tipo_secundario", ""),
                key="dcm_tipo_secundario_text",
            )
        else:
            # Se estiver DESMARCADO, garante que o texto customizado seja limpo
            st.session_state.dcm_form_inputs["tipo_secundario"] = ""
        
        st.markdown("---") #
        st.write(f"**Detalhes Específicos para {st.session_state.dcm_form_inputs['tipo_oferta']} (DCM):**") #
        current_selected_offer_for_fields_dcm = st.session_state.dcm_form_inputs["tipo_oferta"] #
        relevant_fields_for_offer_dcm = configs.DCM_OFFER_TYPES_DETAILS.get(current_selected_offer_for_fields_dcm, {}).get("fields", []) #
        for field_key in relevant_fields_for_offer_dcm: #
            default_value = st.session_state.dcm_form_inputs.get(field_key, "") #
            label = field_key.replace("_", " ").capitalize() + ":" #
            if field_key == "lastro": label = "Lastro da Operação:" #
            elif field_key == "remuneracao_titulo": label = "Remuneração do Título:" #
            elif field_key == "amortizacao_principal": label = "Amortização do Principal:" #
            elif field_key == "pagamento_juros": label = "Pagamento de Juros:" #
            elif field_key == "destinacao": #
                label = "Destinação dos Recursos:" #
                st.session_state.dcm_form_inputs[field_key] = st.text_area(label, value=default_value, height=100, key=f"dcm_input_{field_key}") #
                continue #
            elif field_key == "garantias": #
                label = "Garantias da Operação (uma por linha):" #
                st.session_state.dcm_form_inputs[field_key] = st.text_area(label, value=default_value, height=100, key=f"dcm_input_{field_key}") #
                continue #
            elif field_key == "covenants": #
                label = "Covenants da Operação (uma por linha):" #
                st.session_state.dcm_form_inputs[field_key] = st.text_area(label, value=default_value, height=100, key=f"dcm_input_{field_key}") #
                continue #
            elif field_key == "cotas_fidc": label = "Estrutura das Cotas do FIDC:" #
            elif field_key == "serie_cotas_fidc": label = "Série das Cotas:" #
            elif field_key == "gestor_fidc": label = "Gestor do FIDC:" #
            elif field_key == "administrador_fidc": label = "Administrador do FIDC:" #
            elif field_key == "custodiante_fidc": label = "Custodiante do FIDC:" #
            elif field_key == "uso_recursos_debenture": #
                label = "Uso Específico dos Recursos (Debênture):" #
                st.session_state.dcm_form_inputs[field_key] = st.text_area(label, value=default_value, height=100, key=f"dcm_input_{field_key}") #
                continue #
            st.session_state.dcm_form_inputs[field_key] = st.text_input(label, value=default_value, key=f"dcm_input_{field_key}") #