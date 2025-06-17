import streamlit as st
from io import BytesIO

def render_recibo_page():
    """
    Renderiza a página do Gerador de Recibos.
    """
    # --- Inicialização do Estado da Sessão para o Formulário de Recibo ---
    if 'recibo_form_inputs' not in st.session_state:
        st.session_state.recibo_form_inputs = {
            "nome_empresa": "Nome da Empresa Exemplo S.A.",
            "cnpj_empresa": "00.000.000/0001-00",
            "valor_bruto": "1000,00",
            "tipo_servico": "Ex: Estruturação Financeira",
            "nome_operacao": "Ex: Emissão de CRI",
            "calcular_gross_up": False
        }

    st.title("Gerador de Recibos (em desenvolvimento)")
    st.markdown("---")

    # --- Barra Lateral para Controles e Inputs ---
    with st.sidebar:
        st.header("⚙️ Controles do Recibo")
        
        uploaded_template_recibo = st.file_uploader(
            "Selecione o modelo de recibo (.docx)", 
            type="docx", 
            key="recibo_template_uploader"
        )
        st.markdown("---")

        st.subheader("- Preencha as Informações -")

        # --- Campos do Formulário ---
        st.session_state.recibo_form_inputs["nome_empresa"] = st.text_input(
            "Nome da Empresa:",
            value=st.session_state.recibo_form_inputs["nome_empresa"]
        )
        st.session_state.recibo_form_inputs["cnpj_empresa"] = st.text_input(
            "CNPJ da Empresa:",
            value=st.session_state.recibo_form_inputs["cnpj_empresa"]
        )

        # Usando colunas para colocar o checkbox ao lado do campo de valor
        col_valor, col_grossup = st.columns([2, 2])
        with col_valor:
            st.session_state.recibo_form_inputs["valor_bruto"] = st.text_input(
                "Valor Bruto do Serviço (R$):",
                value=st.session_state.recibo_form_inputs["valor_bruto"],
            )
        with col_grossup:
            # Espaçamento para alinhar verticalmente o checkbox
            st.write("")
            st.write("")
            st.session_state.recibo_form_inputs["calcular_gross_up"] = st.checkbox(
                "Gross-up",
                value=st.session_state.recibo_form_inputs["calcular_gross_up"],
                help="Marque para realizar o cálculo de impostos (gross-up) sobre o valor."
            )

        st.session_state.recibo_form_inputs["tipo_servico"] = st.text_input(
            "Tipo do Serviço Prestado:",
            value=st.session_state.recibo_form_inputs["tipo_servico"]
        )
        st.session_state.recibo_form_inputs["nome_operacao"] = st.text_input(
            "Nome da Operação:",
            value=st.session_state.recibo_form_inputs["nome_operacao"]
        )

        st.markdown("---")
        
        # Botão para gerar o documento (lógica ainda não implementada)
        if st.button("Gerar Recibo", use_container_width=True, type="primary"):
            if uploaded_template_recibo is None:
                st.error("❌ Por favor, selecione um arquivo de modelo (.docx).")
            else:
                st.warning("A lógica de geração de recibos ainda será implementada.")
                # Futuramente, a lógica de geração virá aqui.
                # Ex: doc_gerado = gerar_documento_recibo(...)
                #     st.download_button(...)

    # --- Área Principal ---
    st.info("Preencha os dados na barra lateral à esquerda para gerar o recibo.")
    st.write("As chaves para o documento são:")
    st.code("""
        - Nome da Empresa:  [[Nome_Empresa]]
        - CNPJ da Empresa:  [[CNPJ_Empresa]]
        - Valor Bruto:      [[Valor]]
        - Tipo do Serviço:  [[Tipo]]
        - Nome da Operação: [[Nome]]
            """)