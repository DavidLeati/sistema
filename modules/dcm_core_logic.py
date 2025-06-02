from datetime import datetime, timedelta
from num2words import num2words
from dateutil.relativedelta import relativedelta

# --- Offer Types Configuration ---
OFFER_TYPES_DETAILS = {
    "CRI": {
        "extenso": "Certificados de Recebíveis Imobiliários",
        "gender": "m",
        "fields": ["lastro", "remuneracao_titulo", "amortizacao_principal", "pagamento_juros", "destinacao", "garantias"]
    },
    "CRA": {
        "extenso": "Certificados de Recebíveis do Agronegócio",
        "gender": "m",
        "fields": ["lastro", "remuneracao_titulo", "amortizacao_principal", "pagamento_juros", "destinacao", "garantias"]
    },
    "Debênture": {
        "extenso": "Debêntures",
        "gender": "f",
        "fields": ["remuneracao_titulo", "amortizacao_principal", "pagamento_juros", "destinacao", "garantias", "uso_recursos_debenture"]
    },
    "FIDC": {
        "extenso": "Fundo de Investimento em Direitos Creditórios",
        "gender": "m",
        "fields": ["cotas_fidc", "serie_cotas_fidc", "gestor_fidc", "administrador_fidc", "custodiante_fidc", "remuneracao_titulo", "amortizacao_principal", "pagamento_juros", "destinacao", "garantias"]
    }
}
OFFER_TYPE_OPTIONS = list(OFFER_TYPES_DETAILS.keys())

def format_cep(cep_str: str) -> str:
    """
    Formata uma string de CEP para o formato XXXXX-XXX.
    Retorna a string original se não puder ser formatada como um CEP de 8 dígitos.
    """
    if cep_str and isinstance(cep_str, str):
        cleaned_cep = "".join(filter(str.isdigit, cep_str))
        if len(cleaned_cep) == 8:
            return f"{cleaned_cep[:5]}-{cleaned_cep[5:]}"
    return cep_str

def prepare_document_data(inputs: dict) -> tuple[dict, set, dict]:
    """
    Prepara todos os dados dinâmicos para o template do documento.
    Retorna um dicionário de substituições, um conjunto de chaves para negrito,
    e um dicionário com informações para validação/UI.
    """
    validation_info = {"errors": [], "warnings": []}
    
    valor_total = 0.0
    remuneracao_percent_float = 0.0

    valor_total_input_str = inputs["valor_total_str"]
    if not valor_total_input_str.strip():
        validation_info["errors"].append("'Valor Total da Operação' não pode estar vazio.")
    else:
        try:
            valor_total = float(valor_total_input_str.replace(".", "").replace(",", "."))
        except ValueError:
            validation_info["errors"].append(f"Valor Total da Operação inválido: '{valor_total_input_str}'. Use formato como 10.000.000,00.")

    remuneracao_percent_str_input = inputs["remuneracao_str"]
    if not remuneracao_percent_str_input.strip():
        validation_info["errors"].append("'Remuneração da Estruturação (%)' não pode estar vazio.")
    else:
        try:
            remuneracao_percent_float = float(remuneracao_percent_str_input.replace(",", "."))
        except ValueError:
            validation_info["errors"].append(f"Remuneração da Estruturação (%) inválida: '{remuneracao_percent_str_input}'. Use formato como 0,50 ou 2.")

    if validation_info["errors"]: # Se houver erros de conversão, não prossegue com cálculos dependentes
        return {}, set(), validation_info

    data_hoje = datetime.now()
    dia = data_hoje.day
    meses_pt = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
                "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    mes = meses_pt[data_hoje.month - 1]
    ano = data_hoje.year
    valor_total_ext = num2words(valor_total, lang='pt_BR', to='currency')
    remuneracao_placeholder_val = f"{remuneracao_percent_float:.2f}".replace(".", ",")
    
    raw_remuneracao_input_for_ext = inputs["remuneracao_str"].strip()
    parts = raw_remuneracao_input_for_ext.split(',')
    texto_inteiro = ""
    try:
        parte_inteira_val = int(parts[0])
        texto_inteiro = num2words(parte_inteira_val, lang='pt_BR')
    except ValueError:
        validation_info["errors"].append(f"Parte inteira da remuneração percentual inválida: {parts[0]}")
        # Retorna aqui se a parte inteira for crucial para o restante
        return {}, set(), validation_info


    remuneracao_ext_val = ""
    if len(parts) > 1 and parts[1].strip():
        parte_decimal_str_raw = parts[1].strip()
        try:
            if all(d == '0' for d in parte_decimal_str_raw): # Ex: "1,00" ou "2,0"
                remuneracao_ext_val = f"{texto_inteiro} por cento"
            else:
                texto_decimal = ""
                # Trata casos como "0,05" (zero vírgula zero cinco) vs "0,50" (zero vírgula cinquenta)
                if parte_decimal_str_raw.startswith('0') and len(parte_decimal_str_raw) > 1 and int(parte_decimal_str_raw) !=0 :
                    texto_decimal_parts = []
                    for digit_char in parte_decimal_str_raw: # Converte cada dígito
                        texto_decimal_parts.append(num2words(int(digit_char), lang='pt_BR'))
                    texto_decimal = " ".join(texto_decimal_parts)
                elif int(parte_decimal_str_raw) == 0: # Se a parte decimal for apenas "0" ou "00"
                     texto_decimal = "" # Não adiciona "zero" explicitamente aqui
                else:
                    texto_decimal = num2words(int(parte_decimal_str_raw), lang='pt_BR')
                
                if texto_decimal: # Adiciona "vírgula decimal" apenas se houver texto decimal
                    remuneracao_ext_val = f"{texto_inteiro} vírgula {texto_decimal} por cento"
                else: # Caso de "1,0" ou "1,00"
                    remuneracao_ext_val = f"{texto_inteiro} por cento"

        except ValueError:
            validation_info["errors"].append(f"Parte decimal da remuneração percentual inválida: {parte_decimal_str_raw}")
            return {}, set(), validation_info
    else:
        remuneracao_ext_val = f"{texto_inteiro} por cento"
    remuneracao_ext_val = remuneracao_ext_val.capitalize()

    data_1ano_obj = data_hoje + relativedelta(years=1)
    data_1ano_ext = f'{data_1ano_obj.day} de {meses_pt[data_1ano_obj.month - 1]} de {data_1ano_obj.year}'
    data_20dias_obj = data_hoje + timedelta(days=20)
    data_20dias_ext = f'{data_20dias_obj.day} de {meses_pt[data_20dias_obj.month - 1]} de {data_20dias_obj.year}'

    current_offer_type_key = inputs["tipo_oferta"]
    offer_details = OFFER_TYPES_DETAILS.get(current_offer_type_key, {"gender": "m"}) # Default to 'm' if not found
    artigo_definido_tipo_oferta = "o" if offer_details["gender"] == "m" else "a"
    contracao_de_tipo_oferta = "do" if offer_details["gender"] == "m" else "da"

    endereco_completo_devedora = inputs["endereco_devedora"]
    if inputs["end_num_devedora"] and inputs["end_num_devedora"].strip():
        endereco_completo_devedora += f", nº {inputs['end_num_devedora'].strip()}"
    
    # Checagens de campos obrigatórios que não impediram conversões acima
    required_fields_check = {
        "devedora": "Nome da Devedora",
        "cnpj_devedora": "CNPJ da Devedora",
        "cidade_devedora": "Cidade da Devedora",
        "estado_devedora": "Estado da Devedora",
        "prazo": "Prazo da Operação",
        "destinacao": "Destinação dos Recursos",
        "remuneracao_titulo": "Remuneração do Título",
        "amortizacao_principal": "Amortização do Principal",
        "pagamento_juros": "Pagamento de Juros",
        "garantias": "Garantias da Operação",
        "signatario_nome": "Nome do Signatário",
        "signatario_email": "E-mail do Signatário",
        "emissora": "Nome da Emissora",
        "cnpj_emissora": "CNPJ da Emissora",
    }
    for field, label in required_fields_check.items():
        if not inputs.get(field,"").strip():
            validation_info["warnings"].append(f"Campo '{label}' está vazio ou não preenchido.")


    data_to_replace = {
        "[[Dia]]": str(dia), "[[Mes]]": str(mes), "[[Ano]]": str(ano),
        "[[Devedora]]": inputs["devedora"], "[[CNPJ_Devedora]]": inputs["cnpj_devedora"],
        "[[Tipo_Oferta]]": inputs["tipo_oferta"],
        "[[Cidade_Devedora]]": inputs["cidade_devedora"],
        "[[Estado_Devedora]]": inputs["estado_devedora"].upper(),
        "[[Endereco_Completo_Devedora]]": endereco_completo_devedora,
        "[[Bairro_Devedora]]": inputs["bairro_devedora"],
        "[[CEP_Devedora]]": inputs["cep_devedora"], # Já formatado na entrada da API ou manual
        "[[Tipo_Oferta_Ext]]": inputs["tipo_oferta_ext"],
        "[[Valor_Total]]": f"{valor_total:_.2f}".replace("_", "X").replace(".", ",").replace("X", "."),
        "[[Valor_Total_Ext]]": valor_total_ext.capitalize(),
        "[[Remuneracao]]": remuneracao_placeholder_val,
        "[[Remuneracao_Ext]]": remuneracao_ext_val,
        "[[Data_1ano]]": data_1ano_ext, "[[Data_20dias]]": data_20dias_ext,
        "[[Signatario_Nome]]": inputs["signatario_nome"], "[[Signatario_Email]]": inputs["signatario_email"],
        "[[Emissora]]": inputs["emissora"], "[[Prazo]]": inputs["prazo"],
        "[[Destinacao]]": inputs["destinacao"],
        "[[Remuneracao_Titulo]]": inputs["remuneracao_titulo"],
        "[[Amor_Princ]]": inputs["amortizacao_principal"],
        "[[Pgto_Juros]]": inputs["pagamento_juros"],
        "[[Garantias]]": inputs["garantias"],
        "[[CNPJ_Emissora]]": inputs["cnpj_emissora"],
        "[[Copia_Nome]]": inputs.get("copia_nome", ""), "[[Copia_Email]]": inputs.get("copia_email", ""),
        "[[Artigo_Tipo_Oferta]]": artigo_definido_tipo_oferta,
        "[[Contracao_De_Tipo_Oferta]]": contracao_de_tipo_oferta,
        "[[Lastro]]": inputs.get("lastro", ""),
        "[[Uso_Recursos_Debenture]]": inputs.get("uso_recursos_debenture", ""),
        "[[Cotas_FIDC]]": inputs.get("cotas_fidc", ""),
        "[[Serie_Cotas_FIDC]]": inputs.get("serie_cotas_fidc", ""),
        "[[Gestor_FIDC]]": inputs.get("gestor_fidc", ""),
        "[[Administrador_FIDC]]": inputs.get("administrador_fidc", ""),
        "[[Custodiante_FIDC]]": inputs.get("custodiante_fidc", ""),
    }

    placeholders_to_bold = {
        "[[Devedora]]", "[[Emissora]]", "[[Valor_Total]]",
        "[[Tipo_Oferta_Ext]]",
    }
    return data_to_replace, placeholders_to_bold, validation_info