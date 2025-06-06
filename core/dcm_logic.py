# proposal_system/core/dcm_logic.py
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from shared_utils.text_utils import valor_por_extenso_reais, numero_por_extenso
from shared_utils.formatting_utils import format_cep
from config import configs

def prepare_document_data(inputs: dict) -> tuple[dict, set, dict]:
    validation_info = {"errors": [], "warnings": []}
    
    valor_total = 0.0
    remuneracao_percent_float = 0.0

    valor_total_input_str = inputs["valor_total_str"]
    if not valor_total_input_str.strip():
        validation_info["errors"].append("'Valor Total da Operação' não pode estar vazio.")
    else:
        try:
            valor_total = float(valor_total_input_str.replace(".", "").replace(",", ".")) #
        except ValueError: #
            validation_info["errors"].append(f"Valor Total da Operação inválido: '{valor_total_input_str}'. Use formato como 10.000.000,00.") #

    remuneracao_percent_str_input = inputs["remuneracao_str"] #
    if not remuneracao_percent_str_input.strip(): #
        validation_info["errors"].append("'Remuneração da Estruturação (%)' não pode estar vazio.") #
    else:
        try:
            remuneracao_percent_float = float(remuneracao_percent_str_input.replace(",", ".")) #
        except ValueError: #
            validation_info["errors"].append(f"Remuneração da Estruturação (%) inválida: '{remuneracao_percent_str_input}'. Use formato como 0,50 ou 2.") #

    if validation_info["errors"]: # Se houver erros de conversão, não prossegue com cálculos dependentes #
        return {}, set(), validation_info #

    data_hoje = datetime.now() #
    dia = data_hoje.day #
    mes = configs.MESES_PT[data_hoje.month - 1] #
    ano = data_hoje.year #
    
    # Usando o utilitário de shared_utils
    valor_total_ext_str = valor_por_extenso_reais(valor_total) #
    
    remuneracao_placeholder_val = f"{remuneracao_percent_float:.2f}".replace(".", ",") #
    
    raw_remuneracao_input_for_ext = inputs["remuneracao_str"].strip() #
    parts = raw_remuneracao_input_for_ext.split(',') #
    texto_inteiro = "" #
    try:
        parte_inteira_val = int(parts[0]) #
        texto_inteiro = numero_por_extenso(parte_inteira_val) #
    except ValueError: #
        validation_info["errors"].append(f"Parte inteira da remuneração percentual inválida: {parts[0]}") #
        return {}, set(), validation_info #

    remuneracao_ext_val = "" #
    if len(parts) > 1 and parts[1].strip(): #
        parte_decimal_str_raw = parts[1].strip() #
        try:
            if all(d == '0' for d in parte_decimal_str_raw): # Ex: "1,00" ou "2,0" #
                remuneracao_ext_val = f"{texto_inteiro} por cento" #
            else:
                texto_decimal = "" #
                if parte_decimal_str_raw.startswith('0') and len(parte_decimal_str_raw) > 1 and int(parte_decimal_str_raw) !=0 : #
                    texto_decimal_parts = [] #
                    for digit_char in parte_decimal_str_raw: # Converte cada dígito #
                        texto_decimal_parts.append(numero_por_extenso(int(digit_char))) #
                    texto_decimal = " ".join(texto_decimal_parts) #
                elif int(parte_decimal_str_raw) == 0: # Se a parte decimal for apenas "0" ou "00" #
                     texto_decimal = ""  #
                else:
                    texto_decimal = numero_por_extenso(int(parte_decimal_str_raw)) #
                
                if texto_decimal: # Adiciona "vírgula decimal" apenas se houver texto decimal #
                    remuneracao_ext_val = f"{texto_inteiro} vírgula {texto_decimal} por cento" #
                else: # Caso de "1,0" ou "1,00" #
                    remuneracao_ext_val = f"{texto_inteiro} por cento" #

        except ValueError: #
            validation_info["errors"].append(f"Parte decimal da remuneração percentual inválida: {parte_decimal_str_raw}") #
            return {}, set(), validation_info #
    else:
        remuneracao_ext_val = f"{texto_inteiro} por cento" #
    remuneracao_ext_val = remuneracao_ext_val.capitalize() #

    data_1ano_obj = data_hoje + relativedelta(years=1) #
    data_1ano_ext = f'{data_1ano_obj.day} de {configs.MESES_PT[data_1ano_obj.month - 1]} de {data_1ano_obj.year}' #
    data_20dias_obj = data_hoje + timedelta(days=20) #
    data_20dias_ext = f'{data_20dias_obj.day} de {configs.MESES_PT[data_20dias_obj.month - 1]} de {data_20dias_obj.year}' #

    current_offer_type_key = inputs["tipo_oferta"] #
    offer_details = configs.DCM_OFFER_TYPES_DETAILS.get(current_offer_type_key, {"gender": "m"}) # Default to 'm' if not found #
    artigo_definido_tipo_oferta = "os" if offer_details["gender"] == "m" else "as" #
    artigo_definido_tipo_oferta_cap = "Os" if offer_details["gender"] == "m" else "As" #
    contracao_de_tipo_oferta = "dos" if offer_details["gender"] == "m" else "das" #

    endereco_completo_devedora = inputs["endereco_devedora"] #
    if inputs["end_num_devedora"] and inputs["end_num_devedora"].strip(): #
        endereco_completo_devedora += f", nº {inputs['end_num_devedora'].strip()}" #
    
    for field, label in configs.DCM_REQUIRED_FIELDS_CHECK.items():
        if not inputs.get(field,"").strip():
            validation_info["warnings"].append(f"Campo '{label}' está vazio ou não preenchido.") #

    data_to_replace = { #
        "[[Dia]]": str(dia), "[[Mes]]": str(mes), "[[Ano]]": str(ano), #
        "[[Terra]]": configs.TERRA_NOME_COMPLETO, #
        "[[Devedora]]": inputs["devedora"], "[[CNPJ_Devedora]]": inputs["cnpj_devedora"], #
        "[[Re]]": str("Proposta para Coordenação, Estruturação e Distribuição de" + " " + inputs["tipo_oferta"]),
        "[[Tipo_Oferta]]": inputs["tipo_oferta"], #
        "[[Cidade_Devedora]]": inputs["cidade_devedora"], #
        "[[Estado_Devedora]]": inputs["estado_devedora"].upper(), #
        "[[Endereco_Completo_Devedora]]": endereco_completo_devedora, #
        "[[Bairro_Devedora]]": inputs["bairro_devedora"], #
        "[[CEP_Devedora]]": inputs["cep_devedora"], # Já formatado na entrada da API ou manual #
        "[[Tipo_Oferta_Ext]]": inputs["tipo_oferta_ext"], #
        "[[Valor_Total]]": f"{valor_total:_.2f}".replace("_", "X").replace(".", ",").replace("X", "."), #
        "[[Valor_Total_Ext]]": valor_total_ext_str, #
        "[[Remuneracao]]": remuneracao_placeholder_val, #
        "[[Remuneracao_Ext]]": remuneracao_ext_val, #
        "[[Data_1ano]]": data_1ano_ext, "[[Data_20dias]]": data_20dias_ext, #
        "[[Signatario_Nome]]": inputs["signatario_nome"], "[[Signatario_Email]]": inputs["signatario_email"], #
        "[[Emissora]]": inputs["emissora"], "[[Prazo]]": inputs["prazo"], #
        "[[Destinacao]]": inputs["destinacao"], #
        "[[Remuneracao_Titulo]]": inputs["remuneracao_titulo"], #
        "[[Amor_Princ]]": inputs["amortizacao_principal"], #
        "[[Pgto_Juros]]": inputs["pagamento_juros"], #
        "[[Garantias]]": inputs["garantias"], #
        "[[Covenants]]": inputs.get("covenants", ""), # Atualizado para usar .get() para Covenants
        "[[CNPJ_Emissora]]": inputs["cnpj_emissora"], #
        "[[Copia_Nome]]": inputs.get("copia_nome", ""), "[[Copia_Email]]": inputs.get("copia_email", ""), #
        "[[Artigo_Tipo_Oferta]]": artigo_definido_tipo_oferta, #
        "[[Artigo_Tipo_Oferta_Cap]]": artigo_definido_tipo_oferta_cap, #
        "[[Contracao_De_Tipo_Oferta]]": contracao_de_tipo_oferta,
        "[[Lastro]]": inputs.get("lastro", ""),
        "[[Uso_Recursos_Debenture]]": inputs.get("uso_recursos_debenture", ""),
    }

    return data_to_replace, configs.DCM_PLACEHOLDERS_TO_BOLD, validation_info #