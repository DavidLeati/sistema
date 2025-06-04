import streamlit as st
from io import BytesIO
import traceback
import os
from tempfile import NamedTemporaryFile
from docx2pdf import convert

# Importações dos módulos utilitários
from .. import common_processing_utils # Usando import relativo

def render_coordenacao_page():
    # --- Inicialização do Estado (Específica desta página Coordenação) ---
    if 'coord_form_inputs' not in st.session_state:
        st.session_state.coord_form_inputs = {} # Será preenchido dinamicamente
        # Inicializa com os valores padrão do primeiro tipo de oferta (CRI)
        for label, key, default in common_processing_utils.COORD_FIELD_CONFIGS.get("CRI", []):
            st.session_state.coord_form_inputs[key] = default

    if 'coord_offer_type' not in st.session_state:
        st.session_state.coord_offer_type = "CRI" # Tipo de oferta padrão

    # --- Barra Lateral para Coordenação ---
    with st.sidebar:
        st.header("Gerador Coordenação")
        st.subheader("- Selecione o Modelo -")
        uploaded_template_coord = st.file_uploader(
            "Escolha o arquivo de modelo (.docx)",
            type="docx",
            label_visibility="collapsed", # Para não mostrar "Escolha o arquivo..." duas vezes
            key="coord_template_uploader_sidebar" # Chave diferente da principal se houver outra
        )

        st.subheader("- Gerar Proposta -")
        if st.button("Gerar Documento", use_container_width=True, type="primary", key="coord_gerar_proposta_btn_sidebar"):
            if uploaded_template_coord is None: # Verifica o uploader da sidebar
                st.error("❌ Por favor, selecione um arquivo de modelo (.docx) na barra lateral.")
            else:
                with st.spinner(f"Gerando proposta de Coordenação ({st.session_state.coord_offer_type})... Por favor, aguarde."):
                    try:
                        # Coletar inputs relevantes para o tipo de oferta atual
                        current_inputs = {}
                        # Certifique-se que current_fields_config está definido antes de usar
                        current_fields_config_sidebar = common_processing_utils.COORD_FIELD_CONFIGS.get(st.session_state.coord_offer_type, [])
                        for _, key, _ in current_fields_config_sidebar:
                            current_inputs[key] = st.session_state.coord_form_inputs.get(key)

                        data_to_replace, errors = common_processing_utils.prepare_coordenacao_data(
                            current_inputs,
                            st.session_state.coord_offer_type
                        )

                        if errors:
                            for error_msg in errors:
                                st.error(f"⚠️ Erro de Entrada (Coordenação): {error_msg}")
                        else:
                            template_file_bytes = BytesIO(uploaded_template_coord.getvalue())
                            placeholders_to_bold = {
                                "[[Devedora]]", "[[Valor_Total]]", "[[Tipo_Oferta_Ext]]", "[[Terra]]"
                            }
                            generated_doc_io = common_processing_utils.generate_docx_coordenacao(
                                template_file_bytes,
                                data_to_replace,
                                placeholders_to_bold,
                            )

                            emissora_nome = current_inputs.get("coord_emissora", "Proposta")
                            base_filename = f"Proposta_Coord_{st.session_state.coord_offer_type}_{emissora_nome.replace(' ','_')}"
                            output_filename_docx = f"{base_filename}.docx"

                            st.success(f"✅ Proposta de Coordenação '{output_filename_docx}' gerada!")
                            st.download_button(
                                label=f"⬇️ Baixar Proposta ({st.session_state.coord_offer_type}) (.docx)",
                                data=generated_doc_io,
                                file_name=output_filename_docx,
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                use_container_width=True,
                                key="coord_download_btn_sidebar_docx" # Chave alterada
                            )

                            # --- INÍCIO DA SEÇÃO DE CONVERSÃO PARA PDF ---
                            st.info("⚙️ Tentando converter para PDF...")
                            try:
                                with NamedTemporaryFile(delete=False, suffix=".docx") as tmp_docx_file:
                                    tmp_docx_file.write(generated_doc_io.getvalue())
                                    tmp_docx_path = tmp_docx_file.name

                                output_filename_pdf = f"{base_filename}.pdf"

                                with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf_outfile:
                                    tmp_pdf_out_path = tmp_pdf_outfile.name

                                convert(tmp_docx_path, tmp_pdf_out_path)

                                with open(tmp_pdf_out_path, "rb") as f_pdf:
                                    pdf_bytes = f_pdf.read()

                                st.success(f"✅ Proposta de Coordenação '{output_filename_pdf}' convertida para PDF!")
                                st.download_button(
                                    label=f"⬇️ Baixar Proposta ({st.session_state.coord_offer_type}) (.pdf)",
                                    data=BytesIO(pdf_bytes),
                                    file_name=output_filename_pdf,
                                    mime="application/pdf",
                                    use_container_width=True,
                                    key="coord_download_btn_sidebar_pdf"
                                )
                                os.unlink(tmp_docx_path)
                                os.unlink(tmp_pdf_out_path)

                            except Exception as pdf_e:
                                st.error(f"❌ Falha ao converter para PDF: {pdf_e}")
                                st.error(f"Detalhes do erro de PDF: {traceback.format_exc()}")
                         
                            # --- FIM DA SEÇÃO DE CONVERSÃO PARA PDF ---

                    except Exception as e:
                        st.error(f"❌ Ocorreu um erro crítico ao gerar a proposta de Coordenação: {e}")
                        st.error(f"Detalhes do erro: {traceback.format_exc()}")

    # --- Conteúdo Principal da Página "Gerador de Propostas de Coordenação" ---
    st.subheader("Gerador de Propostas de Coordenação") # Título no corpo principal

    # Seleção do Tipo de Oferta (Coordenação)
    coord_offer_options = list(common_processing_utils.COORD_FIELD_CONFIGS.keys())

    def on_coord_offer_type_change():
        new_offer_type = st.session_state.coord_offer_type_selector_main
        st.session_state.coord_offer_type = new_offer_type
        current_config = common_processing_utils.COORD_FIELD_CONFIGS.get(new_offer_type, [])
        for label_text, key_name, default_val in current_config:
            if key_name not in st.session_state.coord_form_inputs or st.session_state.coord_form_inputs.get(f"{key_name}_offer_type") != new_offer_type :
                 st.session_state.coord_form_inputs[key_name] = default_val
                 st.session_state.coord_form_inputs[f"{key_name}_offer_type"] = new_offer_type

    selected_coord_offer_type = st.selectbox(
        "Selecione o Tipo de Oferta (Coordenação):",
        options=coord_offer_options,
        index=coord_offer_options.index(st.session_state.coord_offer_type),
        key="coord_offer_type_selector_main", # Chave diferente para o selectbox principal
        on_change=on_coord_offer_type_change
    )
    if st.session_state.coord_offer_type_selector_main != st.session_state.coord_offer_type:
        st.session_state.coord_offer_type = st.session_state.coord_offer_type_selector_main
        # A função on_change já deve tratar a atualização dos defaults.
        # Considerar st.rerun() se os defaults não atualizarem visualmente de imediato.

    st.markdown("---")

    st.subheader(f"Dados para Proposta de Coordenação: {st.session_state.coord_offer_type}")

    current_fields_config_main = common_processing_utils.COORD_FIELD_CONFIGS.get(st.session_state.coord_offer_type, [])

    col1, col2 = st.columns(2)

    for i, (label, key, default_value) in enumerate(current_fields_config_main):
        target_col = col1 if i % 2 == 0 else col2
        with target_col:
            widget_key = f"{key}_{st.session_state.coord_offer_type}_main"

            if widget_key not in st.session_state.coord_form_inputs:
                st.session_state.coord_form_inputs[widget_key] = st.session_state.coord_form_inputs.get(key, default_value)

            if key == "coord_garantias" or key == "coord_destinacao":
                st.session_state.coord_form_inputs[key] = st.text_area( 
                    label,
                    value=st.session_state.coord_form_inputs[widget_key], 
                    key=widget_key
                )
            else:
                st.session_state.coord_form_inputs[key] = st.text_input( 
                    label,
                    value=st.session_state.coord_form_inputs[widget_key], 
                    key=widget_key
                )

    st.markdown("---")