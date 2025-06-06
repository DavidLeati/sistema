# proposal_system/ui/coordenacao_page.py
import streamlit as st
from io import BytesIO
import traceback #

# Importações dos módulos refatorados
from core import coordenacao_logic # Alterado de common_processing_utils
from document_processing import document_generator
from config import configs

def render_coordenacao_page():
    # --- Inicialização do Session State para os artefatos gerados ---
    if "coord_process_complete" not in st.session_state:
        st.session_state.coord_process_complete = False
    if "coord_generated_doc_io" not in st.session_state:
        st.session_state.coord_generated_doc_io = None
    if "coord_output_filename_docx" not in st.session_state:
        st.session_state.coord_output_filename_docx = None
    if "coord_error_message" not in st.session_state:
        st.session_state.coord_error_message = None
    if 'coord_form_inputs' not in st.session_state: 
        st.session_state.coord_form_inputs = {} 
    
        for label, key, default in configs.COORD_FIELD_CONFIGS.get("CRI", []): 
            st.session_state.coord_form_inputs[key] = default 

    if 'coord_offer_type' not in st.session_state: #
        st.session_state.coord_offer_type = "CRI" #

    with st.sidebar: #
        st.header("Gerador Coordenação") #
        st.subheader("- Selecione o Modelo -") #
        uploaded_template_coord = st.file_uploader( #
            "Escolha o arquivo de modelo (.docx)", #
            type="docx", #
            label_visibility="collapsed", #
            key="coord_template_uploader_sidebar" #
        )

        st.subheader("- Gerar Proposta -")
        if st.button("Gerar Documento", use_container_width=True, type="primary", key="coord_gerar_proposta_btn_sidebar"):
            # Resetar estados anteriores
            st.session_state.coord_process_complete = False
            st.session_state.coord_generated_doc_io = None
            st.session_state.coord_output_filename_docx = None
            st.session_state.coord_error_message = None

            if uploaded_template_coord is None:
                st.error("❌ Por favor, selecione um arquivo de modelo (.docx) na barra lateral.")
                st.session_state.coord_process_complete = True # Marca que a tentativa terminou
            else:
                with st.spinner(f"Gerando proposta de Coordenação ({st.session_state.coord_offer_type})... Por favor, aguarde."):
                    try:
                        current_inputs = {}
                        current_fields_config_sidebar = configs.COORD_FIELD_CONFIGS.get(st.session_state.coord_offer_type, [])
                        for _, key, _ in current_fields_config_sidebar:
                            current_inputs[key] = st.session_state.coord_form_inputs.get(key)

                        data_to_replace, errors = coordenacao_logic.prepare_coordenacao_data(
                            current_inputs,
                            st.session_state.coord_offer_type
                        )

                        if errors:
                            for error_msg in errors:
                                st.error(f"⚠️ Erro de Entrada (Coordenação): {error_msg}")
                            st.session_state.coord_process_complete = True
                            return # Sai da lógica do botão

                        template_file_bytes = BytesIO(uploaded_template_coord.getvalue())
                        
                        generated_doc_io = document_generator.generate_coordenacao_document(
                            template_file_bytes,
                            data_to_replace,
                            configs.COORD_PLACEHOLDERS_TO_BOLD,
                        )
                        st.session_state.coord_generated_doc_io = generated_doc_io

                        emissora_nome = current_inputs.get("coord_emissora", "Proposta")
                        base_filename = f"Proposta_Coord_{st.session_state.coord_offer_type}_{emissora_nome.replace(' ','_')}"
                        st.session_state.coord_output_filename_docx = f"{base_filename}.docx"

                    except Exception as e:
                        st.session_state.coord_error_message = f"❌ Ocorreu um erro crítico ao gerar a proposta de Coordenação: {e}\nDetalhes: {traceback.format_exc()}"
                    finally:
                        st.session_state.coord_process_complete = True # Marca que o processo terminou

        # --- Exibição dos resultados e botões de download ---
        if st.session_state.coord_process_complete:
            if st.session_state.coord_error_message:
                st.error(st.session_state.coord_error_message)

            if st.session_state.coord_generated_doc_io:
                st.success(f"✅ Proposta de Coordenação '{st.session_state.coord_output_filename_docx}' gerada!")
                st.download_button(
                    label=f"⬇️ Baixar Proposta ({st.session_state.coord_offer_type}) (.docx)",
                    data=st.session_state.coord_generated_doc_io,
                    file_name=st.session_state.coord_output_filename_docx,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                    key="coord_download_btn_sidebar_docx_final" # Chave única para evitar conflitos
                )

    st.subheader("Gerador de Propostas de Coordenação") #

    coord_offer_options = list(coordenacao_logic.COORD_FIELD_CONFIGS.keys()) #

    def on_coord_offer_type_change(): #
        new_offer_type = st.session_state.coord_offer_type_selector_main #
        st.session_state.coord_offer_type = new_offer_type #
        current_config = configs.COORD_FIELD_CONFIGS.get(new_offer_type, []) #
        for label_text, key_name, default_val in current_config: #
            if key_name not in st.session_state.coord_form_inputs or st.session_state.coord_form_inputs.get(f"{key_name}_offer_type") != new_offer_type : #
                 st.session_state.coord_form_inputs[key_name] = default_val #
                 st.session_state.coord_form_inputs[f"{key_name}_offer_type"] = new_offer_type #

    selected_coord_offer_type = st.selectbox( #
        "Selecione o Tipo de Oferta (Coordenação):", #
        options=coord_offer_options, #
        index=coord_offer_options.index(st.session_state.coord_offer_type), #
        key="coord_offer_type_selector_main", #
        on_change=on_coord_offer_type_change #
    )
    if st.session_state.coord_offer_type_selector_main != st.session_state.coord_offer_type: #
        st.session_state.coord_offer_type = st.session_state.coord_offer_type_selector_main #

    st.markdown("---") #

    st.subheader(f"Dados para Proposta de Coordenação: {st.session_state.coord_offer_type}") #

    current_fields_config_main = configs.COORD_FIELD_CONFIGS.get(st.session_state.coord_offer_type, []) #

    col1, col2 = st.columns(2) #

    for i, (label, key, default_value) in enumerate(current_fields_config_main): #
        target_col = col1 if i % 2 == 0 else col2 #
        with target_col: #
            widget_key = f"{key}_{st.session_state.coord_offer_type}_main" #

            if widget_key not in st.session_state.coord_form_inputs: #
                st.session_state.coord_form_inputs[widget_key] = st.session_state.coord_form_inputs.get(key, default_value) #

            if key == "coord_garantias" or key == "coord_destinacao": #
                st.session_state.coord_form_inputs[key] = st.text_area(  #
                    label, #
                    value=st.session_state.coord_form_inputs[widget_key],  #
                    key=widget_key #
                )
            else:
                st.session_state.coord_form_inputs[key] = st.text_input(  #
                    label, #
                    value=st.session_state.coord_form_inputs[widget_key],  #
                    key=widget_key #
                )

    st.markdown("---") #