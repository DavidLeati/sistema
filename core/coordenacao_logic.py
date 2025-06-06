# proposal_system/core/coordenacao_logic.py
from datetime import datetime, timedelta #
from dateutil.relativedelta import relativedelta #
from shared_utils.text_utils import valor_por_extenso_reais, numero_por_extenso, genero_quantidade #
from shared_utils.formatting_utils import format_valor_brl #
from config import configs

def prepare_coordenacao_data(inputs: dict, offer_type: str) -> tuple[dict, list]: #
    errors = [] #
    data_to_replace = {} #

    try:
        valor_total_str = inputs.get("coord_valor_total_str", "0").replace(",", ".") #
        valor_total = float(valor_total_str) #
    except ValueError: #
        errors.append(f"Valor Total inválido: '{inputs.get('coord_valor_total_str', '')}'. Use formato numérico como 100000,00.") #
        valor_total = 0.0 #

    try:
        remuneracao_str = inputs.get("coord_remuneracao_str", "0").replace(",", ".") #
        remuneracao_valor = float(remuneracao_str) #
    except ValueError: #
        errors.append(f"Remuneração inválida: '{inputs.get('coord_remuneracao_str', '')}'. Use formato numérico como 60000,00.") #
        remuneracao_valor = 0.0 #

    if errors: #
        return {}, errors #

    data_hoje = datetime.now() #
    dia = data_hoje.day #
    mes = configs.MESES_PT[data_hoje.month - 1] #
    ano = data_hoje.year  #

    valor_total_ext_str = valor_por_extenso_reais(valor_total).lower() #
    
    qtd_total = valor_total / 1000 #
    qtd_total_ext_str = numero_por_extenso(qtd_total) #
    qtd_total_ext_str = genero_quantidade(qtd_total_ext_str + ' cotas') # # Utiliza genero_quantidade de text_utils

    remuneracao_ext_str = valor_por_extenso_reais(remuneracao_valor) #

    data_1ano_obj = data_hoje + relativedelta(years=1)  #
    data_1ano_ext = f'{data_1ano_obj.day} de {configs.MESES_PT[data_1ano_obj.month - 1]} de {data_1ano_obj.year}'  #

    data_20dias_obj = data_hoje + timedelta(days=20)  #
    data_20dias_ext = f'{data_20dias_obj.day} de {configs.MESES_PT[data_20dias_obj.month - 1]} de {data_20dias_obj.year}'  #

    valor_total_fmt_str = format_valor_brl(valor_total) #
    remuneracao_fmt_str = format_valor_brl(remuneracao_valor) #
    qtd_total_fmt_str = f"{qtd_total:_.0f}".replace("_", "X").replace(".", ",").replace("X", ".") #


    data_to_replace = { #
        "[[Dia]]": str(dia),
        "[[Mes]]": str(mes),
        "[[Ano]]": str(ano),
        "[[Terra]]": configs.TERRA_NOME_COMPLETO,
        "[[Emissora]]": inputs.get("coord_emissora", ""),
        "[[CNPJ_Emissora]]": inputs.get("coord_cnpj_emissora", ""),
        "[[Copia]]": inputs.get("coord_copia_nome", ""),
        "[[Email_Copia]]": inputs.get("coord_copia_email", ""),
        "[[Valor_Total]]": valor_total_fmt_str,
        "[[Valor_Total_Ext]]": valor_total_ext_str,
        "[[Qtd_Total]]": qtd_total_fmt_str,
        "[[Qtd_Total_Ext]]": qtd_total_ext_str,
        "[[Remuneracao]]": remuneracao_fmt_str,
        "[[Remuneracao_Ext]]": remuneracao_ext_str,
        "[[Data_1ano]]": data_1ano_ext,
        "[[Data_20dias]]": data_20dias_ext,
        "[[Prazo]]": inputs.get("coord_prazo", ""),  #
        "[[Remuneracao_Titulo]]": inputs.get("coord_remuneracao_titulo", ""),  #
        "[[Amor_Princ]]": inputs.get("coord_amortizacao_principal", ""), #
        "[[Pgto_Juros]]": inputs.get("coord_pagamento_juros", ""), #
        "[[Garantias]]": inputs.get("coord_garantias", ""), #
    }

    if offer_type in ["CRI", "CRA"]: #
        data_to_replace["[[Lastro]]"] = inputs.get("coord_lastro", "")  #
        data_to_replace["[[Devedora]]"] = inputs.get("coord_devedora", "")  #
        data_to_replace["[[Destinacao]]"] = inputs.get("coord_destinacao", "")  #
        data_to_replace["[[Assessor]]"] = inputs.get("coord_assessor_legal", "")  #
    
    return data_to_replace, errors #